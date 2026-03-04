import requests
import uuid

BASE_URL = "http://127.0.0.1:8000"

def test_status_transitions():
    # 1. Setup Admin and Ruleset
    alias = f"admin_{uuid.uuid4().hex[:4]}"
    requests.post(f"{BASE_URL}/auth/signup", json={"alias": alias, "password": "password"})
    login_resp = requests.post(f"{BASE_URL}/auth/login", json={"alias": alias, "password": "password"}).json()
    admin_id = login_resp["id"]
    
    rs_resp = requests.post(f"{BASE_URL}/rulesets/", json={
        "name": "Standard Round",
        "win_points": 3, "draw_points": 1, "kill_points": 0, "allows_custom_achievements": False
    }).json()
    ruleset_id = rs_resp["id"]

    # 2. Create Event (Status: PENDING)
    event_resp = requests.post(f"{BASE_URL}/events/", json={
        "title": "Status Transition Test",
        "organizer_id": admin_id,
        "ruleset_id": ruleset_id
    }).json()
    event_id = event_resp["id"]
    join_code = event_resp["join_code"]
    print(f"Initial Status: {event_resp.get('status')}") # Should be pending

    # 3. Add 4 players (Needed for a pod)
    for i in range(4):
        requests.post(f"{BASE_URL}/auth/guest_join", json={
            "alias": f"player_{i}_{uuid.uuid4().hex[:4]}",
            "join_code": join_code
        })

    # 4. Generate Round (Status should change to ACTIVE)
    print("Generating first round...")
    gen_resp = requests.post(f"{BASE_URL}/matchmaking/events/{event_id}/generate-round")
    
    # Check current status
    status_resp = requests.get(f"{BASE_URL}/matchmaking/events/{event_id}").json()
    print(f"Status after round generation: {status_resp.get('status')}")

    # 5. Close the active round first
    print("Closing the active round...")
    round_id = gen_resp.json().get("round", {}).get("id")
    # Need to report some winners or just close it? 
    # Usually you need to report winners, but let's see if we can just close it if we fix the backend or do it here.
    # Actually, let's use the close-round endpoint.
    requests.post(f"{BASE_URL}/matchmaking/events/{event_id}/close-round")

    # 6. Close Event (Status should change to COMPLETED)
    print("Closing event...")
    close_resp = requests.post(f"{BASE_URL}/matchmaking/events/{event_id}/close-event")
    print(f"Close result: {close_resp.json().get('message')}")


    # Final Check
    final_status_resp = requests.get(f"{BASE_URL}/matchmaking/events/{event_id}").json()
    print(f"Final Status: {final_status_resp.get('status')}")

if __name__ == "__main__":
    test_status_transitions()
