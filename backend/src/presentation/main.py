from fastapi import FastAPI, HTTPException
from typing import List
import uuid
from datetime import datetime, UTC
from presentation.routers.matchmaking import router as matchmaking_router 
from application.schemas import UserCreate, UserResponse, EventCreate, EventResponse, FormatRulesetCreate, FormatRulesetResponse, EventRegistrationRequest
from domain.entities import User, Event, FormatRuleset, EventStatus
import secrets

# Inicializamos la instacia de nuestra aplicación
app = FastAPI(
    title="Rule Zero API",
    description="Backend para App Commander MTG",
    version="1.0.0"
)
app.include_router(matchmaking_router)
# Endpoint básico de estado (Health Check)
@app.get("/")
def health_check():
    """Ruta para verificar que el servidor está funcionando."""
    return {"status": "ok", "message": "Rule Zero API is running"}

# Base de datos en memoria temporal (simula Infrastructure)
fake_users_db: List[User] = []
fake_events_db: List[Event] = []
fake_rulesets_db: List[FormatRuleset] = []

@app.post("/users/", response_model=UserResponse)
def create_user(user_in: UserCreate):
    """
    Crea un nuevo usuario en el sistema.
    Pydantic validará automáticamente el alias y el email.
    """
    # 1. Transformamos los datos que entran (DTO) a nuestro modelo de Dominio
    new_user = User(
        id=str(uuid.uuid4()),  # Generamos ID único
        alias=user_in.alias,
        email=user_in.email,
        is_guest=user_in.is_guest
    )
    
    # 2. Guardamos en nuestra "base de datos"
    fake_users_db.append(new_user)
    
    # 3. Devolvemos la entidad de dominio; Pydantic la transformará en UserResponse (gracias a from_attributes=True)
    return new_user

@app.post("/events/", response_model=EventResponse)
def create_event(event_in: EventCreate):
    """
    Crea un nuevo torneo/evento.
    La validación (title, ruleset_id, organizer_id) la hace Pydantic.
    """
    # Aquí podríamos (y deberíamos en el futuro) tener un Caso de Uso que:
    # 1. Compruebe si organizer_id existe en fake_users_db
    # 2. Compruebe si ruleset_id existe en fake_rulesets_db
    
    nuevo_evento = Event(
        id=str(uuid.uuid4()),          # El backend genera el ID
        title=event_in.title,          # Viene valiado por Pydantic
        organizer_id=event_in.organizer_id,
        ruleset_id=event_in.ruleset_id,
        status=EventStatus.PENDING,    # Lógica de negocio: empiezan PENDING
        created_at=datetime.now(UTC),
        join_code=secrets.token_hex(3).upper(),   # Generamos un código de invitación único   # Le asignamos la hora de creación (UTC)
        players=[]
    )
    
    fake_events_db.append(nuevo_evento)
    return nuevo_evento

@app.post("/rulesets/", response_model=FormatRulesetResponse)
def create_ruleset(ruleset_in: FormatRulesetCreate):
    """Crea una nueva tabla de reglas y puntos para un formato."""
    nuevo_ruleset = FormatRuleset(
        id=str(uuid.uuid4()),
        name=ruleset_in.name,
        win_points=ruleset_in.win_points,
        draw_points=ruleset_in.draw_points,
        kill_points=ruleset_in.kill_points,
        allows_custom_achievements=ruleset_in.allows_custom_achievements
    )
    fake_rulesets_db.append(nuevo_ruleset)
    return nuevo_ruleset

@app.post("/events/register")
def register_to_event(data: EventRegistrationRequest):
    # Aquí irá la magia...
    event=next((e for e in fake_events_db if e.join_code == data.join_code), None)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    if event.status != EventStatus.PENDING:
        raise HTTPException(status_code=400, detail="El evento ya ha comenzado o ha finalizado")
    if data.user_id not in event.players:
        event.players.append(data.user_id)
    return event