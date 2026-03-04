import requests
import uuid

BASE_URL = "http://127.0.0.1:8000"

def debug_leaderboard():
    # 1. Setup
    alias = f"admin_{uuid.uuid4().hex[:4]}"
    requests.post(f"{BASE_URL}/auth/signup", json={"alias": alias, "password": "password"})
    login_resp = requests.post(f"{BASE_URL}/auth/login", json={"alias": alias, "password": "password"}).json()
    admin_id = login_resp["id"]
    
    rs_resp = requests.post(f"{BASE_URL}/rulesets/", json={
        "name": "Debug RS",
        "win_points": 3, "draw_points": 1, "kill_points": 0, "allows_custom_achievements": False
    }).json()
    ruleset_id = rs_resp["id"]

    event_resp = requests.post(f"{BASE_URL}/events/", json={
        "title": "LB Debug",
        "organizer_id": admin_id,
        "ruleset_id": ruleset_id
    }).json()
    event_id = event_resp["id"]
    join_code = event_resp["join_code"]

    # 2. Add a player
    print(f"Adding player to event {event_id}...")
    requests.post(f"{BASE_URL}/auth/guest_join", json={
        "alias": "Player1",
        "join_code": join_code
    })

    # Extra: check event info
    event_info = requests.get(f"{BASE_URL}/matchmaking/events/{event_id}").json()
    print(f"Event Players: {event_info.get('players')}")


    # 3. Check Leaderboard
    print(f"Checking leaderboard for event {event_id}...")
    resp = requests.get(f"{BASE_URL}/matchmaking/events/{event_id}/leaderboard")
    print(f"Status: {resp.status_code}")
    print(f"Content: {resp.json()}")

if __name__ == "__main__":
    debug_leaderboard()
