from pydantic import BaseModel, EmailStr, Field
from typing import Optional

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
