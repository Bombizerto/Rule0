from fastapi import FastAPI, HTTPException, Request
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import uuid
import traceback
from datetime import datetime, UTC
from presentation.routers.matchmaking import router as matchmaking_router 
from application.schemas import UserCreate, UserResponse, EventCreate, EventResponse, FormatRulesetCreate, FormatRulesetResponse, EventRegistrationRequest, LoginRequest, LoginResponse, GuestJoinRequest, RegisterRequest
from domain.entities import User, Role, Event, FormatRuleset, EventStatus, PlayerStatus
from infrastructure.database import get_db, engine
from infrastructure.models_orm import Base
from infrastructure.repositories import UserRepository, EventRepository, FormatRulesetRepository
from sqlalchemy.orm import Session
from fastapi import Depends
import secrets

# Inicializamos las tablas (en desarrollo)
Base.metadata.create_all(bind=engine)

# Inicializamos la instacia de nuestra aplicación
app = FastAPI(
    title="Rule Zero API",
    description="Backend para App Commander MTG",
    version="1.0.0"
)

# Configuración de CORS dinámica
# allow_credentials=False porque usamos auth por JSON body, no cookies.
# allow_origins=["*"] permite cualquier frontend (localhost, Vercel, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(matchmaking_router)

# Handler global para que los errores 500 incluyan cabeceras CORS
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    print(f"⚠️ ERROR NO CONTROLADO: {exc}\n{tb}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"},
    )

# Endpoint básico de estado (Health Check)
@app.get("/")
def health_check():
    """Ruta para verificar que el servidor está funcionando."""
    return {"status": "ok", "message": "Rule Zero API is running"}

@app.post("/debug/seed")
def seed_database():
    """Puebla la base de datos con datos de prueba automáticamente."""
    from infrastructure.seed import seed_test_data
    seed_test_data()
    return {"message": "Database seeded successfully", "event_id": "test-event-123"}

@app.post("/users/", response_model=UserResponse)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo usuario en el sistema.
    Pydantic validará automáticamente el alias y el email.
    """
    # 1. Transformamos los datos que entran (DTO) a nuestro modelo de Dominio
    new_user = User(
        id=str(uuid.uuid4()),  # Generamos ID único
        alias=user_in.alias,
        password="password", # Default temporal
        email=user_in.email,
        is_guest=user_in.is_guest,
        role=user_in.role
    )
    
    # 2. Guardamos en nuestra base de datos
    repo = UserRepository(db)
    repo.save(new_user)
    
    # 3. Devolvemos la entidad de dominio; Pydantic la transformará en UserResponse (gracias a from_attributes=True)
    return new_user

@app.post("/events/", response_model=EventResponse)
def create_event(event_in: EventCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo torneo/evento.
    La validación (title, ruleset_id, organizer_id) la hace Pydantic.
    """
    nuevo_evento = Event(
        id=str(uuid.uuid4()),          # El backend genera el ID
        title=event_in.title,          # Viene valiado por Pydantic
        organizer_id=event_in.organizer_id,
        ruleset_id=event_in.ruleset_id,
        status=EventStatus.PENDING,    # Lógica de negocio: empiezan PENDING
        created_at=datetime.now(UTC),
        join_code=secrets.token_hex(3).upper(),   # Generamos un código de invitación único
        players=[],
        rounds=[],
        player_status={}
    )
    
    repo = EventRepository(db)
    repo.save(nuevo_evento)
    return nuevo_evento

@app.post("/rulesets/", response_model=FormatRulesetResponse)
def create_ruleset(ruleset_in: FormatRulesetCreate, db: Session = Depends(get_db)):
    """Crea una nueva tabla de reglas y puntos para un formato."""
    nuevo_ruleset = FormatRuleset(
        id=str(uuid.uuid4()),
        name=ruleset_in.name,
        win_points=ruleset_in.win_points,
        draw_points=ruleset_in.draw_points,
        kill_points=ruleset_in.kill_points,
        allows_custom_achievements=ruleset_in.allows_custom_achievements
    )
    repo = FormatRulesetRepository(db)
    repo.save(nuevo_ruleset)
    return nuevo_ruleset

@app.post("/events/register")
def register_to_event(data: EventRegistrationRequest, db: Session = Depends(get_db)):
    repo = EventRepository(db)
    event = repo.get_by_join_code(data.join_code)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    if event.status != EventStatus.PENDING:
        raise HTTPException(status_code=400, detail="El evento ya ha comenzado o ha finalizado")
    if data.user_id not in event.players:
        event.players.append(data.user_id)
        # SQLAlchemy and dict mutability require care, but we replace the entire object logic for saving.
        # Ensure we don't just mutate the dict implicitly if it causes tracking issues, but our mapper handles it.
        event.player_status[data.user_id] = PlayerStatus.ACTIVE
        repo.save(event)
    return event

@app.get("/events/organizer/{organizer_id}", response_model=List[Event])
def get_events_by_organizer(organizer_id: str, db: Session = Depends(get_db)):
    """
    Lista todos los torneos que pertenecen a un organizador específico.
    """
    repo = EventRepository(db)
    return repo.get_by_organizer(organizer_id)

@app.post("/auth/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    repo = UserRepository(db)
    user = repo.get_by_alias(request.alias)
    if not user or user.password != request.password:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    return {
        "id": user.id,
        "alias": user.alias,
        "role": user.role,
        "is_guest": user.is_guest,
        "message": "Login successful"
    }

@app.post("/auth/signup", response_model=LoginResponse)
def signup(request: RegisterRequest, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    
    # Validar alias único
    existing_user = user_repo.get_by_alias(request.alias)
    if existing_user:
        raise HTTPException(status_code=400, detail="Este nombre ya está en uso. Por favor, elige otro.")
        
    # Registrar usuario asignando Rol Player (o Admin si existiera lógica, por ahora se asigna por defecto)
    new_user = User(
        id=str(uuid.uuid4()),
        alias=request.alias,
        password=request.password,
        is_guest=False,
        role=Role.PLAYER
    )
    user_repo.save(new_user)
    
    return {
        "id": new_user.id,
        "alias": new_user.alias,
        "role": new_user.role,
        "is_guest": new_user.is_guest,
        "message": "Cuenta creada con éxito"
    }

@app.post("/auth/guest_join", response_model=LoginResponse)
def guest_join(request: GuestJoinRequest, db: Session = Depends(get_db)):
    event_repo = EventRepository(db)
    user_repo = UserRepository(db)
    
    # Validar torneo
    event = event_repo.get_by_join_code(request.join_code)
    if not event:
        raise HTTPException(status_code=404, detail="Torneo no encontrado")
    if event.status != EventStatus.PENDING:
        raise HTTPException(status_code=400, detail="El evento ya ha comenzado")
        
    # Validar alias único
    existing_user = user_repo.get_by_alias(request.alias)
    if existing_user:
        raise HTTPException(status_code=400, detail="Este nombre ya está en uso. Por favor, elige otro.")
        
    # Registrar usuario
    new_user = User(
        id=str(uuid.uuid4()),
        alias=request.alias,
        is_guest=True,
        role=Role.PLAYER
    )
    user_repo.save(new_user)
    
    # Inscribir a evento
    event.players.append(new_user.id)
    event.player_status[new_user.id] = PlayerStatus.ACTIVE
    event_repo.save(event)
    
    return {
        "id": new_user.id,
        "alias": new_user.alias,
        "role": new_user.role,
        "is_guest": True,
        "message": "Invitado unido con éxito"
    }

@app.get("/events/player/{player_id}", response_model=List[Event])
def get_events_by_player(player_id: str, db: Session = Depends(get_db)):
    repo = EventRepository(db)
    return repo.get_by_player(player_id)

@app.get("/events/{event_id}/players-info")
def get_players_info(event_id: str, db: Session = Depends(get_db)):
    """Devuelve la lista de jugadores inscritos en un evento con su alias resuelto."""
    event_repo = EventRepository(db)
    user_repo = UserRepository(db)
    
    event = event_repo.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    players_info = []
    for player_id in event.players:
        user = user_repo.get_by_id(player_id)
        players_info.append({
            "id": player_id,
            "alias": user.alias if user else player_id
        })
    
    return players_info
