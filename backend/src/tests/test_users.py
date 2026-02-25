import pytest
from fastapi.testclient import TestClient

# Importamos nuestra app para poder hacerle peticiones falsas
from presentation.main import app, fake_users_db
from domain.entities import User
from application.schemas import UserCreate

client = TestClient(app)

def setup_function():
    """Limpia la base de datos falsa antes de cada test."""
    fake_users_db.clear()

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

def test_presentation_create_user_endpoint():
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
    assert len(fake_users_db) == 1
