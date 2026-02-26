from dataclasses import dataclass, field
from typing import Optional, List, Dict
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
    seat_history: Dict[int, int] = field(default_factory=lambda: {1: 0, 2: 0, 3: 0, 4: 0})

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

@dataclass
class Pod:
    """Representa una mesa de juego con sus jugadores asignados."""
    id: str
    table_number: int
    players_ids: List[str]
    winner_id: Optional[str] = None
    
@dataclass
class Round:
    """Representa una ronda de un evento."""
    id: str
    event_id: str
    round_number: int
    pods: List[Pod]
    is_active: bool = True
    created_at: Optional[datetime] = None
