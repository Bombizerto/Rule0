from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from domain.entities import EventStatus, PlayerStatus, Role

class UserBase(BaseModel):
    """Atributos compartidos por todos los esquemas de Usuario."""
    alias: str = Field(..., min_length=2, max_length=50, description="El nombre que se mostrará en la mesa.")
    email: Optional[EmailStr] = None
    is_guest: bool = False
    role: Role = Role.PLAYER

class UserCreate(UserBase):
    """Esquema para validar los datos que entran cuando se crea un usuario."""
    pass

class UserResponse(UserBase):
    """Esquema para controlar lo que devolvemos hacia el cliente (Frontend)."""
    id: str
    
    class Config:
        from_attributes = True  # Permite a Pydantic leer datos directamente de nuestros objetos/clases del Dominio

# --- SCHEMAS DE REGLAS (FormatRuleset) ---
class FormatRulesetBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    win_points: int = 3
    draw_points: int = 1
    kill_points: int = 0
    allows_custom_achievements: bool = False
class FormatRulesetCreate(FormatRulesetBase):
    pass
class FormatRulesetResponse(FormatRulesetBase):
    id: str
    model_config = ConfigDict(from_attributes=True)
# --- SCHEMAS DE EVENTOS (Event) ---
class EventBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=100)
    organizer_id: str
    ruleset_id: str
class EventCreate(EventBase):
    """Datos necesarios para crear un evento."""
    pass
class EventPlayerResponse(BaseModel):
    """Datos de cada jugador dentro del contexto de un evento"""
    id: str
    alias: str
    status: str

class PodResponse(BaseModel):
    id: str
    table_number: int
    players_ids: List[str]
    winner_id: Optional[str] = None
    is_draw: bool = False
    proposed_winner_id: Optional[str] = None
    proposed_is_draw: bool = False
    confirmations: dict = Field(default_factory=dict)
    is_disputed: bool = False
    model_config = ConfigDict(from_attributes=True)

class RoundResponse(BaseModel):
    id: str
    event_id: str
    round_number: int
    pods: List[PodResponse]
    is_active: bool = True
    model_config = ConfigDict(from_attributes=True)


class EventResponse(EventBase):
    """Datos que devolvemos al frontend sobre un evento."""
    id: str
    status: EventStatus
    join_code: str
    players: List[EventPlayerResponse]
    rounds: List[RoundResponse]
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class EventRegistrationRequest(BaseModel):
    user_id: str
    join_code: str

class PodWinnerReport(BaseModel):
    winner_id: str

class PodProposeResultRequest(BaseModel):
    player_id: str
    winner_id: Optional[str] = None
    is_draw: bool = False

class PodConfirmResultRequest(BaseModel):
    player_id: str

class PodRejectResultRequest(BaseModel):
    player_id: str

class PlayerStatusUpdate(BaseModel):
    player_id: str
    status: str

class PlayerLoginRequest(BaseModel):
    join_code: str
    player_alias: str
    password: str

class LoginRequest(BaseModel):
    alias: str
    password: str

class RegisterRequest(BaseModel):
    alias: str
    password: str

class LoginResponse(BaseModel):
    id: str
    alias: str
    role: Role
    is_guest: bool
    device_token: Optional[str] = None  # Solo se devuelve para invitados al crearse
    message: str

class GuestJoinRequest(BaseModel):
    alias: str
    join_code: str
    device_token: Optional[str] = None  # Enviado por el cliente para re-login
