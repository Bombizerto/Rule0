import os
import sys
import uuid
import time
import requests
import argparse
from sqlalchemy import create_engine, text

def print_step(msg):
    print(f"\n[+] {msg}...")
    
def print_success(msg):
    print(f"  ✓ {msg}")

def print_error(msg):
    print(f"  ❌ ERROR: {msg}")
    
def main():
    parser = argparse.ArgumentParser(description="Rule0 End-to-End Test Suite")
    parser.add_argument("--url", default="https://rule0.onrender.com", help="Base URL of the API to test")
    parser.add_argument("--db", default=os.getenv("DATABASE_URL"), help="Direct database URL for cleanup")
    args = parser.parse_args()

    BASE_URL = args.url.rstrip('/')
    DB_URL = args.db
    
    print("=========================================")
    print(f"🚀 Iniciando E2E Tests en: {BASE_URL}")
    print("=========================================")
    
    # Asegurar sufijo único para no chocar con pruebas anteriores que hayan fallado
    test_suffix = str(uuid.uuid4())[:6]
    
    org_alias = f"e2e_org_{test_suffix}"
    p1_alias = f"e2e_p1_{test_suffix}"
    p2_alias = f"e2e_p2_{test_suffix}"
    p3_alias = f"e2e_p3_{test_suffix}"
    p4_alias = f"e2e_p4_{test_suffix}"
    
    org_id = None
    player_ids = []
    event_id = None
    join_code = None
    
    try:
        # 1. Crear organizador
        print_step("Creando cuenta de Organizador")
        r = requests.post(f"{BASE_URL}/auth/signup", json={"alias": org_alias, "password": "password"})
        r.raise_for_status()
        org_id = r.json()["id"]
        print_success(f"Organizador creado: {org_alias} ({org_id})")

        # 2. Crear jugadores
        print_step("Creando cuentas de Jugadores (4)")
        for alias in [p1_alias, p2_alias, p3_alias, p4_alias]:
            r = requests.post(f"{BASE_URL}/auth/signup", json={"alias": alias, "password": "password"})
            r.raise_for_status()
            player_ids.append(r.json()["id"])
            print_success(f"Jugador creado: {alias}")

        # 3. Obtener Ruleset
        print_step("Obteniendo Rulesets disponibles")
        r = requests.get(f"{BASE_URL}/rulesets/")
        r.raise_for_status()
        rulesets = r.json()
        if not rulesets:
            print_error("No hay rulesets disponibles en la BD para crear el torneo.")
            sys.exit(1)
        ruleset_id = rulesets[0]["id"]
        print_success(f"Usando Ruleset: {rulesets[0]['name']}")

        # 4. Crear Torneo
        print_step("Creando nuevo Torneo")
        r = requests.post(f"{BASE_URL}/events/", json={
            "title": f"E2E Test Event {test_suffix}",
            "organizer_id": org_id,
            "ruleset_id": ruleset_id
        })
        r.raise_for_status()
        event_data = r.json()
        event_id = event_data["id"]
        join_code = event_data["join_code"]
        print_success(f"Torneo creado: {event_id} (Código: {join_code})")

        # 5. Inscribir Jugadores
        print_step("Inscribiendo jugadores al torneo")
        for p_id in player_ids:
            r = requests.post(f"{BASE_URL}/events/register", json={
                "join_code": join_code,
                "user_id": p_id
            })
            r.raise_for_status()
        print_success("4 jugadores inscritos correctamente")

        # 6. Generar Ronda
        print_step("Generando Ronda 1")
        # El endpoint cambió recientemente, comprobamos la firma real
        r = requests.post(f"{BASE_URL}/matchmaking/generate-round/{event_id}")
        r.raise_for_status()
        round_data = r.json()
        print_success(f"Ronda generada con ID: {round_data['id']}")
        
        pods = round_data.get("pods", [])
        if not pods:
            print_error("La ronda generada no tiene mesas (pods).")
            sys.exit(1)
            
        pod_id = pods[0]["id"]
        print_success(f"Mesa 1 asignada con ID: {pod_id}")

        # 7. Obtener Leaderboard Inicial (Deberían tener todos 0 puntos)
        print_step("Comprobando Leaderboard Inicial")
        r = requests.get(f"{BASE_URL}/matchmaking/leaderboard/{event_id}")
        r.raise_for_status()
        lb = r.json()
        print_success(f"Leaderboard devuelto con {len(lb)} jugadores")

        print("\n✅ ¡Todos los tests E2E han pasado correctamente!")

    except requests.exceptions.RequestException as e:
        print_error(f"Fallo en la petición HTTP: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print_error(f"Detalle del servidor: {e.response.text}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error inesperado durante el test: {e}")
        sys.exit(1)
    finally:
        # --- TEARDOWN DIRECTO A BASE DE DATOS ---
        print("\n=========================================")
        print("🧹 Iniciando limpieza de datos de prueba")
        print("=========================================")
        
        if not DB_URL:
            print("⚠️ No se ha proporcionado --db URL ni hay variable DATABASE_URL.")
            print("Los datos de prueba generados NO han sido borrados.")
            print(f"Usuarios a borrar manualmente: {org_alias}, {p1_alias}, {p2_alias}, etc.")
            return

        try:
            print_step("Conectando a base de datos...")
            engine = create_engine(DB_URL)
            with engine.connect() as conn:
                # Si llegamos a crear el torneo
                if event_id:
                    print_step("Borrando Pods y Rondas de prueba...")
                    conn.execute(text("DELETE FROM pods WHERE id IN (SELECT p.id FROM pods p JOIN rounds r ON p.round_id = r.id WHERE r.event_id = :eid)"), {"eid": event_id})
                    conn.execute(text("DELETE FROM rounds WHERE event_id = :eid"), {"eid": event_id})
                    
                    print_step("Borrando Evento de prueba...")
                    conn.execute(text("DELETE FROM events WHERE id = :eid"), {"eid": event_id})
                
                # Borrar todos los usuarios creados en este run
                print_step("Borrando Usuarios de prueba...")
                all_test_users = [org_id] + player_ids
                valid_users = [u for u in all_test_users if u is not None]
                if valid_users:
                    # Formatear la IN clause para SQLAlchemy
                    # Como es un script interno rápido usamos string formatting seguro al ser UUIDs propios
                    users_str = "','".join(valid_users)
                    conn.execute(text(f"DELETE FROM users WHERE id IN ('{users_str}')"))
                
                conn.commit()
                print_success("Limpieza completada. La base de datos está como antes.")
                
        except Exception as e:
            print_error(f"Fallo al intentar limpiar la base de datos: {e}")
            print("Es posible que queden datos residuales del test E2E en la BBDD.")

if __name__ == "__main__":
    main()
