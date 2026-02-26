from fastapi import APIRouter, HTTPException
from domain.services.create_round import create_round
from domain.entities import User # Lo necesitaremos para los tipos
from infrastructure.database import fake_events_db, fake_users_db

router = APIRouter(prefix="/matchmaking", tags=["Matchmaking"])

@router.post("/events/{event_id}/generate-round")
async def generate_round_endpoint(event_id: str):
    """
    Endpoint para generar una nueva ronda de forma automática.
    """
    event=next((e for e in fake_events_db if e.id == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    players=[user for user in fake_users_db if user.id in event.players]
    
    if len(players)<3:
        raise HTTPException(status_code=400, detail="No hay suficientes jugadores para generar una ronda")
    new_round=create_round(event_id, event.round_number+1, players)
    event.rounds.append(new_round)
    event.round_number+=1

    return {
        "round": new_round,
        "message": f"Generando ronda para el evento {event_id}",
        "status": "pairing"
    }