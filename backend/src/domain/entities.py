from dataclasses import dataclass
from typing import Optional

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
