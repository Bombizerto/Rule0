import pytest
from pydantic import ValidationError
from datetime import datetime, UTC
from domain.entities import Event, FormatRuleset, EventStatus, PlayerStatus
from application.schemas import EventCreate, FormatRulesetCreate
from infrastructure.repositories import EventRepository

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
        ruleset_id="ruleset-1",
        join_code="A1B2C3",
        players=[]
    )
    assert evento.status == EventStatus.PENDING
    assert evento.created_at is None
    assert evento.join_code == "A1B2C3"
    assert len(evento.players) == 0

def test_application_event_schema_validation():
    """Prueba que el título del evento debe tener mínimo 5 caracteres."""
    with pytest.raises(ValidationError):
        EventCreate(title="Test", organizer_id="123", ruleset_id="456") # 'Test' tiene 4 letras

def test_presentation_create_event_endpoint(client, db_session):
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
    assert "join_code" in data
    assert len(data["join_code"]) == 6
    assert data["players"] == []
    
    events = EventRepository(db_session).list_all()
    assert len(events) == 1

def test_presentation_rgister_to_event_success(client, db_session):
    """Prueba que un usuario se puede registrar a un evento."""
    fake_event = Event(
        id="evt-1",
        title="Torneo Test",
        organizer_id="org-1",
        ruleset_id="ruleset-1",
        join_code="A1B2C3",
        players=[],
        rounds=[],
        created_at=datetime.now(UTC),
        player_status={}
    )
    EventRepository(db_session).save(fake_event)
    payload = {
        "user_id": "user-123",
        "join_code": "A1B2C3"
    }
    response = client.post("/events/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["players"] == ["user-123"]

def test_presentation_register_to_event_not_found(client, db_session):
    """Prueba que un usuario no se puede registrar a un evento no encontrado."""
    payload = {
        "user_id": "user-123",
        "join_code": "A1B2C3"
    }
    response = client.post("/events/register", json=payload)
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Evento no encontrado"

def test_presentation_register_to_event_already_registered(client, db_session):
    """Prueba que un usuario no se puede registrar a un evento si ya está registrado."""
    fake_event = Event(
        id="evt-1",
        title="Torneo Test",
        organizer_id="org-1",
        ruleset_id="ruleset-1",
        join_code="A1B2C3",
        players=["user-123"],
        rounds=[],
        created_at=datetime.now(UTC),
        player_status={"user-123": PlayerStatus.ACTIVE}
    )
    EventRepository(db_session).save(fake_event)
    payload = {
        "user_id": "user-123",
        "join_code": "A1B2C3"
    }
    response = client.post("/events/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["players"] == ["user-123"]

def test_presentation_register_to_event_already_started(client, db_session):
    """Prueba que un usuario no se puede registrar a un evento si ya ha comenzado."""
    fake_event = Event(
        id="evt-1",
        title="Torneo Test",
        organizer_id="org-1",
        ruleset_id="ruleset-1",
        join_code="A1B2C3",
        players=["user-123"],
        rounds=[],
        created_at=datetime.now(UTC),
        player_status={"user-123": PlayerStatus.ACTIVE},
        status=EventStatus.ACTIVE
    )
    EventRepository(db_session).save(fake_event)
    payload = {
        "user_id": "user-123",
        "join_code": "A1B2C3"
    }
    response = client.post("/events/register", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "El evento ya ha comenzado o ha finalizado"

def test_presentation_register_to_event_already_finished(client, db_session):
    """Prueba que un usuario no se puede registrar a un evento si ya ha finalizado."""
    fake_event = Event(
        id="evt-1",
        title="Torneo Test",
        organizer_id="org-1",
        ruleset_id="ruleset-1",
        join_code="A1B2C3",
        players=["user-123"],
        rounds=[],
        created_at=datetime.now(UTC),
        player_status={"user-123": PlayerStatus.ACTIVE},
        status=EventStatus.COMPLETED
    )
    EventRepository(db_session).save(fake_event)
    payload = {
        "user_id": "user-123",
        "join_code": "A1B2C3"
    }
    response = client.post("/events/register", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "El evento ya ha comenzado o ha finalizado"

def test_presentation_get_events_by_organizer_success(client, db_session):
    """Prueba que el organizador puede recuperar sus eventos correctamente."""
    repo = EventRepository(db_session)
    # Añadimos un par de eventos a la base de datos falsa
    now = datetime.now(UTC)
    repo.save(Event(
            id="evt-org-1",
            title="Torneo Organizer 1",
            organizer_id="org-555",
            ruleset_id="ruleset-1",
            join_code="ORG555",
            players=[],
            rounds=[],
            created_at=now,
            player_status={}
        ))
    repo.save(Event(
            id="evt-org-2",
            title="Torneo Organizer 2",
            organizer_id="org-555",
            ruleset_id="ruleset-1",
            join_code="ORG556",
            players=[],
            rounds=[],
            created_at=now,
            player_status={}
        ))
    repo.save(Event(
            id="evt-org-3",
            title="Torneo Otro",
            organizer_id="org-666",
            ruleset_id="ruleset-1",
            join_code="ORG666",
            players=[],
            rounds=[],
            created_at=now,
            player_status={}
        ))
    
    response = client.get("/events/organizer/org-555")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["organizer_id"] == "org-555"
    assert data[1]["organizer_id"] == "org-555"

def test_presentation_get_events_by_organizer_empty(client, db_session):
    """Prueba que devuelve una lista vacía si el organizador no tiene eventos."""
    response = client.get("/events/organizer/org-no-events")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0

