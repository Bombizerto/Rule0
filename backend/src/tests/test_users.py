import pytest
from domain.entities import User
from application.schemas import UserCreate
from infrastructure.repositories import UserRepository

def test_domain_user_creation():
    """Prueba que una Entidad de Dominio se crea correctamente."""
    user = User(id="123", alias="JugadorTest", email="test@test.com")
    assert user.alias == "JugadorTest"
    assert user.is_guest is False

def test_application_schema_validation():
    """Prueba que Pydantic rechaza correos inválidos."""
    # Debería fallar si el correo es inválido
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        UserCreate(alias="Jugador2", email="correo_invalido")

def test_presentation_create_user_endpoint(client, db_session):
    """Prueba que el endpoint /users/ funciona y devuelve código 200."""
    respuesta = client.post("/users/", json={
        "alias": "Jugador3",
        "email": "jugador3@test.com",
        "is_guest": True
    })
    
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["alias"] == "Jugador3"
    assert "id" in datos
    
    repo = UserRepository(db_session)
    user = repo.get_by_id(datos["id"])
    assert user is not None
    assert user.alias == "Jugador3"
