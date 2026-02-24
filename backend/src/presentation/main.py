from fastapi import FastAPI
from typing import List
import uuid
# Aquí estamos importando la CAPA APPLICATION desde la Presentation
from application.schemas import UserCreate, UserResponse
# Y también nuestro DOMINIO
from domain.entities import User
# Inicializamos la instacia de nuestra aplicación
app = FastAPI(
    title="Rule Zero API",
    description="Backend para App Commander MTG",
    version="1.0.0"
)

# Endpoint básico de estado (Health Check)
@app.get("/")
def health_check():
    """Ruta para verificar que el servidor está funcionando."""
    return {"status": "ok", "message": "Rule Zero API is running"}
# Base de datos en memoria temporal (simula Infrastructure)
fake_users_db: List[User] = []
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