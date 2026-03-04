import os
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from infrastructure.database import Base, SQLALCHEMY_DATABASE_URL
from infrastructure.models_orm import UserModel, EventModel, FormatRulesetModel, RoundModel, PodModel
from domain.entities import Role, EventStatus, PlayerStatus
import json

def migrate():
    # 1. Conexión a SQLite (Origen)
    # Buscamos el archivo local que esté en la raíz del backend
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    sqlite_path = os.path.join(BASE_DIR, "rule0.db")
    
    if not os.path.exists(sqlite_path):
        print(f"❌ Error: No se encuentra el archivo SQLite en {sqlite_path}")
        return

    print(f"📂 Leyendo datos desde SQLite: {sqlite_path}")
    
    # 2. Conexión a PostgreSQL (Destino - vía SQLAlchemy)
    if "sqlite" in SQLALCHEMY_DATABASE_URL and not os.getenv("DATABASE_URL"):
        print("❌ Error: La DATABASE_URL no está configurada para PostgreSQL.")
        print("Usa: set DATABASE_URL=postgresql://user:pass@host:port/dbname (Windows)")
        print("O: export DATABASE_URL=... (Linux/Mac)")
        return

    print(f"🚀 Conectando a la base de datos de destino...")
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    # 3. Crear tablas en destino
    print("🏗️ Creando tablas en el destino...")
    Base.metadata.create_all(engine)

    # 4. Función auxiliar para leer SQLite
    def query_sqlite(query):
        conn = sqlite3.connect(sqlite_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        return rows

    try:
        # --- MIGRAR RULESETS ---
        print("📦 Migrando Rulesets...")
        rulesets = query_sqlite("SELECT * FROM format_rulesets")
        for r in rulesets:
            obj = FormatRulesetModel(
                id=r['id'],
                name=r['name'],
                win_points=r['win_points'],
                draw_points=r['draw_points'],
                kill_points=r['kill_points'],
                allows_custom_achievements=bool(r['allows_custom_achievements'])
            )
            session.merge(obj)

        # --- MIGRAR USERS ---
        print("👤 Migrando Usuarios...")
        users = query_sqlite("SELECT * FROM users")
        for u in users:
            obj = UserModel(
                id=u['id'],
                alias=u['alias'],
                password=u['password'],
                email=u['email'],
                is_guest=bool(u['is_guest']),
                role=u['role'],
                seat_history=json.loads(u['seat_history']) if u['seat_history'] else {}
            )
            session.merge(obj)

        # --- MIGRAR EVENTS ---
        print("🏆 Migrando Eventos...")
        events = query_sqlite("SELECT * FROM events")
        for e in events:
            obj = EventModel(
                id=e['id'],
                title=e['title'],
                organizer_id=e['organizer_id'],
                ruleset_id=e['ruleset_id'],
                join_code=e['join_code'],
                players=json.loads(e['players']) if e['players'] else [],
                player_status=json.loads(e['player_status']) if e['player_status'] else {},
                status=e['status'],
                created_at=e['created_at'],
                round_number=e['round_number']
            )
            session.merge(obj)

        # --- MIGRAR ROUNDS ---
        print("🎲 Migrando Rondas...")
        rounds = query_sqlite("SELECT * FROM rounds")
        for r in rounds:
            obj = RoundModel(
                id=r['id'],
                event_id=r['event_id'],
                round_number=r['round_number'],
                is_active=bool(r['is_active']),
                created_at=r['created_at']
            )
            session.merge(obj)

        # --- MIGRAR PODS ---
        print("🃏 Migrando Mesas (Pods)...")
        pods = query_sqlite("SELECT * FROM pods")
        for p in pods:
            obj = PodModel(
                id=p['id'],
                round_id=p['round_id'],
                table_number=p['table_number'],
                players_ids=json.loads(p['players_ids']) if p['players_ids'] else [],
                winner_id=p['winner_id'],
                is_draw=bool(p['is_draw']),
                proposed_winner_id=p['proposed_winner_id'],
                proposed_is_draw=bool(p['proposed_is_draw']),
                confirmations=json.loads(p['confirmations']) if p['confirmations'] else {},
                is_disputed=bool(p['is_disputed'])
            )
            session.merge(obj)

        session.commit()
        print("✅ ¡Migración completada con éxito!")

    except Exception as ex:
        session.rollback()
        print(f"❌ Error durante la migración: {ex}")
    finally:
        session.close()

if __name__ == "__main__":
    migrate()
