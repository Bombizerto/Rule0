from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
from enum import Enum


@dataclass
class User:
    """
    Entidad de Dominio que representa a un Usuario (Jugador u Organizador).
    En Clean Architecture, el dominio no sabe nada de bases de datos ni frameworks.
    """
    id: str  # Simularemos un UUID
    alias: str
    email: Optional[str] = None
    is_guest: bool = False

class EventStatus(str, Enum):
    """Estados posibles para un Evento (Torneo/Liga)."""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"


@dataclass
class FormatRuleset:
    """Define un formato de reglas (Ej. cEDH otorga 4 puntos al ganador, Casual permite logros)."""
    id: str
    name: str
    win_points: int
    draw_points: int
    kill_points: int
    allows_custom_achievements: bool

@dataclass
class Event:
    """Entidad principal de un Evento o Liga."""
    id: str
    title: str
    organizer_id: str  # El ID del usuario que creó el evento
    ruleset_id: str
    join_code: str
    players: List[str]    # ID de las reglas aplicadas
    status: EventStatus = EventStatus.PENDING
    created_at: Optional[datetime] = None
    
