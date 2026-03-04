import requests
import uuid

BASE_URL = "http://127.0.0.1:8000"

def test_player_status_logic():
    # 1. Crear un torneo y un jugador
    # Usaremos el endpoint de signup para un admin y guest_join para el jugador
    admin_alias = f"admin_{uuid.uuid4().hex[:4]}"
    player_alias = f"player_{uuid.uuid4().hex[:4]}"
    
    # Signup admin
    requests.post(f"{BASE_URL}/auth/signup", json={"alias": admin_alias, "password": "password"})
    login_resp = requests.post(f"{BASE_URL}/auth/login", json={"alias": admin_alias, "password": "password"}).json()
    admin_id = login_resp["id"]
    
    # Crear Ruleset primero
    rs_resp = requests.post(f"{BASE_URL}/rulesets/", json={
        "name": "Test Ruleset",
        "win_points": 3,
        "draw_points": 1,
        "kill_points": 0,
        "allows_custom_achievements": False
    }).json()
    ruleset_id = rs_resp["id"]

    # Crear Evento (la ruta es /events/ en main.py, no /matchmaking/events/)
    event_resp = requests.post(f"{BASE_URL}/events/", json={
        "title": "Test Status Event",
        "organizer_id": admin_id,
        "ruleset_id": ruleset_id
    }).json()
    event_id = event_resp["id"]
    join_code = event_resp["join_code"]
    
    # Join Player
    player_resp = requests.post(f"{BASE_URL}/auth/guest_join", json={
        "alias": player_alias,
        "join_code": join_code
    }).json()
    player_id = player_resp["id"]
    
    print(f"Evento: {event_id}, Jugador: {player_id}")
    
    # 2. Probar Auto-Pausa (Player)
    print("\nProbar Auto-Pausa...")
    resp = requests.post(f"{BASE_URL}/matchmaking/events/{event_id}/self_change_status", json={
        "player_id": player_id,
        "status": "paused"
    })
    print(f"Self-Pause: {resp.status_code} - {resp.json().get('message')}")
    
    # 3. Probar Auto-Reactivar (Player)
    print("\nProbar Auto-Reactivar...")
    resp = requests.post(f"{BASE_URL}/matchmaking/events/{event_id}/self_change_status", json={
        "player_id": player_id,
        "status": "active"
    })
    print(f"Self-Reactivate: {resp.status_code} - {resp.json().get('message')}")
    
    # 4. Probar Auto-Drop (Player)
    print("\nProbar Auto-Drop...")
    resp = requests.post(f"{BASE_URL}/matchmaking/events/{event_id}/self_change_status", json={
        "player_id": player_id,
        "status": "dropped"
    })
    print(f"Self-Drop: {resp.status_code} - {resp.json().get('message')}")
    
    # 5. Intentar Auto-Reactivar tras Drop (Debe fallar - 403)
    print("\nIntentar Auto-Reactivar tras Drop (Debe fallar con 403)...")
    resp = requests.post(f"{BASE_URL}/matchmaking/events/{event_id}/self_change_status", json={
        "player_id": player_id,
        "status": "active"
    })
    print(f"Self-Reactivate after Drop: {resp.status_code} - {resp.json().get('detail')}")
    
    # 6. Admin Reactiva (Debe funcionar)
    print("\nAdmin Reactiva...")
    resp = requests.post(f"{BASE_URL}/matchmaking/events/{event_id}/change_player_status", json={
        "player_id": player_id,
        "status": "active"
    })
    if resp.status_code != 200:
        print(f"FAILED Admin-Reactivate: {resp.status_code} - {resp.json()}")
    else:
        print(f"Admin-Reactivate: {resp.status_code} - {resp.json().get('message')}")


if __name__ == "__main__":
    test_player_status_logic()
