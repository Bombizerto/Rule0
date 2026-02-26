from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from domain.entities import EventStatus

class UserBase(BaseModel):
    """Atributos compartidos por todos los esquemas de Usuario."""
    alias: str = Field(..., min_length=2, max_length=50, description="El nombre que se mostrará en la mesa.")
    email: Optional[EmailStr] = None
    is_guest: bool = False

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
class EventResponse(EventBase):
    """Datos que devolvemos al frontend sobre un evento."""
    id: str
    status: EventStatus
    join_code: str
    players: List[str]
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class EventRegistrationRequest(BaseModel):
    user_id: str
    join_code: str

class PodWinnerReport(BaseModel):
    winner_id: str