import pytest
from fastapi.testclient import TestClient
from presentation.main import app
from infrastructure.database import fake_users_db, fake_events_db, fake_rulesets_db
from infrastructure.seed import seed_test_data

client = TestClient(app)

@pytest.fixture
def clean_db():
    fake_users_db.clear()
    fake_events_db.clear()
    fake_rulesets_db.clear()
    seed_test_data()
    yield
    fake_users_db.clear()
    fake_events_db.clear()
    fake_rulesets_db.clear()

def test_generate_round_endpoint(clean_db):
    event_id = "test-event-123"
    response = client.post(f"/matchmaking/events/{event_id}/generate-round")
    assert response.status_code == 200
    data = response.json()
    assert "round" in data
    assert data["status"] == "pairing"

def test_generate_round_not_found(clean_db):
    response = client.post("/matchmaking/events/non-existent/generate-round")
    assert response.status_code == 404

def test_get_event_endpoint(clean_db):
    event_id = "test-event-123"
    response = client.get(f"/matchmaking/events/{event_id}")
    assert response.status_code == 200
    assert response.json()["id"] == event_id

def test_get_active_round_endpoint(clean_db):
    event_id = "test-event-123"
    # Primero generamos una ronda
    client.post(f"/matchmaking/events/{event_id}/generate-round")
    
    response = client.get(f"/matchmaking/events/{event_id}/active-round")
    assert response.status_code == 200
    assert response.json()["event_id"] == event_id

def test_get_active_round_no_rounds(clean_db):
    event_id = "test-event-123"
    response = client.get(f"/matchmaking/events/{event_id}/active-round")
    assert response.status_code == 400 # Error porque no hay rondas

def test_report_winner_endpoint(clean_db):
    event_id = "test-event-123"
    # 1. Generar ronda
    gen_resp = client.post(f"/matchmaking/events/{event_id}/generate-round")
    pod = gen_resp.json()["round"]["pods"][0]
    pod_id = pod["id"]
    winner_id = pod["players_ids"][0]
    
    # 2. Reportar ganador
    report_data = {"winner_id": winner_id}
    response = client.post(f"/matchmaking/pods/{pod_id}/report-winner", json=report_data)
    
    assert response.status_code == 200
    assert response.json()["alias"] is not None

def test_report_winner_invalid_player(clean_db):
    event_id = "test-event-123"
    gen_resp = client.post(f"/matchmaking/events/{event_id}/generate-round")
    pod_id = gen_resp.json()["round"]["pods"][0]["id"]
    
    report_data = {"winner_id": "invalid-id"}
    response = client.post(f"/matchmaking/pods/{pod_id}/report-winner", json=report_data)
    assert response.status_code == 400

def test_get_leaderboard_endpoint(clean_db):
    event_id = "test-event-123"
    # Generar y finalizar ronda
    gen_resp = client.post(f"/matchmaking/events/{event_id}/generate-round")
    round_id = gen_resp.json()["round"]["id"]
    
    # Marcamos la ronda como terminada para que el leaderboard la cuente
    event = next(e for e in fake_events_db if e.id == event_id)
    event.rounds[0].is_active = False
    
    response = client.get(f"/matchmaking/events/{event_id}/leaderboard")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_report_draw_endpoint(clean_db):
    event_id = "test-event-123"
    gen_resp = client.post(f"/matchmaking/events/{event_id}/generate-round")
    pod_id = gen_resp.json()["round"]["pods"][0]["id"]
    
    response = client.post(f"/matchmaking/pods/{pod_id}/report-draw")
    assert response.status_code == 200
    assert "Empate reportado" in response.json()["message"]
