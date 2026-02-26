from fastapi import APIRouter, HTTPException
from domain.services.create_round import create_round
from domain.entities import User # Lo necesitaremos para los tipos

router = APIRouter(prefix="/matchmaking", tags=["Matchmaking"])

@router.post("/events/{event_id}/generate-round")
async def generate_round_endpoint(event_id: str):
    """
    Endpoint para generar una nueva ronda de forma automática.
    """
    # Por ahora, como no tenemos base de datos real, 
    # vamos a devolver un mensaje de éxito simulado.
    return {
        "message": f"Generando ronda para el evento {event_id}",
        "status": "pairing"
    }