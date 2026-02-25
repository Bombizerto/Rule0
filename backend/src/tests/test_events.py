import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from presentation.main import app, fake_events_db, fake_rulesets_db
from domain.entities import Event, FormatRuleset, EventStatus
from application.schemas import EventCreate, FormatRulesetCreate

client = TestClient(app)

def setup_function():
    """Limpia la base de datos falsa antes de cada test."""
    fake_events_db.clear()
    fake_rulesets_db.clear()

# --- TESTS PARA REGLAS (FormatRulesets) ---

def test_domain_ruleset_creation():
    """Prueba que la Entidad de Dominio FormatRuleset se instancia correctamente."""
    ruleset = FormatRuleset(
        id="ruleset-1",
        name="Reglas cEDH",
        win_points=4,
        draw_points=1,
        kill_points=0,
        allows_custom_achievements=False
    )
    assert ruleset.name == "Reglas cEDH"
    assert ruleset.win_points == 4

def test_application_ruleset_schema_validation():
    """Prueba que el nombre del ruleset debe tener al menos 3 caracteres."""
    with pytest.raises(ValidationError):
        FormatRulesetCreate(name="ab") # Muy corto

def test_application_ruleset_schema_defaults():
    """Prueba que los valores por defecto del esquema se aplican bien."""
    ruleset_schema = FormatRulesetCreate(name="Casual")
    assert ruleset_schema.win_points == 3 # Default
    assert ruleset_schema.allows_custom_achievements is False

# --- TESTS PARA EVENTOS (Events) ---

def test_domain_event_creation():
    """Prueba que un Evento del dominio se crea con estado PENDING por defecto."""
    evento = Event(
        id="evt-1",
        title="Torneo Test",
        organizer_id="org-1",
        ruleset_id="ruleset-1"
    )
    assert evento.status == EventStatus.PENDING
    assert evento.created_at is None

def test_application_event_schema_validation():
    """Prueba que el título del evento debe tener mínimo 5 caracteres."""
    with pytest.raises(ValidationError):
        EventCreate(title="Test", organizer_id="123", ruleset_id="456") # 'Test' tiene 4 letras

def test_presentation_create_event_endpoint():
    """Prueba el endpoint /events/ simulando una llamada HTTP."""
    payload = {
        "title": "Torneo de Fin de Semana",
        "organizer_id": "user-123",
        "ruleset_id": "ruleset-99"
    }
    
    response = client.post("/events/", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Torneo de Fin de Semana"
    assert data["status"] == "pending"
    assert "id" in data
    assert "created_at" in data
    assert len(fake_events_db) == 1
