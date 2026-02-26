from fastapi import APIRouter, HTTPException
from domain.services.create_round import create_round
from domain.services.leaderboard import calculate_leaderboard
from domain.entities import User, PlayerStatus, EventStatus # Lo necesitaremos para los tipos
from infrastructure.database import fake_events_db, fake_users_db
from application.schemas import EventResponse, PodWinnerReport, PlayerStatusUpdate

router = APIRouter(prefix="/matchmaking", tags=["Matchmaking"])

@router.post("/events/{event_id}/generate-round")
async def generate_round_endpoint(event_id: str):
    """
    Endpoint para generar una nueva ronda de forma automática.
    """
    event=next((e for e in fake_events_db if e.id == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    players=[user for user in fake_users_db if user.id in event.players and event.player_status[user.id] == PlayerStatus.ACTIVE]
    
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

@router.get("/events/{event_id}", response_model=EventResponse)
def get_event(event_id: str):
    event = next((e for e in fake_events_db if e.id == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return event

@router.get("/events/{event_id}/active-round")
async def get_active_round(event_id: str):
    event = next((e for e in fake_events_db if e.id == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    if not event.rounds:
        raise HTTPException(status_code=400, detail="No hay rondas generadas para este evento")
    
    # Devolvemos la última ronda de la lista
    return event.rounds[-1]

@router.post("/pods/{pod_id}/report-winner", response_model=User)
async def report_winner(pod_id: str, report: PodWinnerReport):
    pod = next((p for event in fake_events_db 
              for round in event.rounds 
              for p in round.pods 
              if p.id == pod_id), None)
    if not pod:
        raise HTTPException(status_code=404, detail="Pod no encontrado")
    ganador=next((u for u in fake_users_db if u.id == report.winner_id), None)
    if(report.winner_id not in pod.players_ids):
        raise HTTPException(status_code=400, detail="El jugador no pertenece a este pod")
    pod.winner_id=report.winner_id
    
    return ganador

@router.get("/events/{event_id}/leaderboard")
def get_leaderboard(event_id: str):
    """Devuelve la clasificación actual del evento."""
    return calculate_leaderboard(event_id)

@router.post("/pods/{pod_id}/report-draw")
async def report_draw(pod_id: str):
    pod = next((p for event in fake_events_db 
              for round in event.rounds 
              for p in round.pods 
              if p.id == pod_id), None)
    if not pod:
        raise HTTPException(status_code=404, detail="Pod no encontrado")
    pod.is_draw = True
    return {"message": f"Empate reportado para el pod {pod_id}"}

@router.post("/events/{event_id}/change_player_status")
def change_player_status(event_id: str, player_status_update: PlayerStatusUpdate):
    event = next((e for e in fake_events_db if e.id == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    if player_status_update.player_id not in event.players:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    if event.status != EventStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="El evento no está activo")
    if player_status_update.status not in PlayerStatus:
        raise HTTPException(status_code=400, detail="Estado de jugador no válido")
    event.player_status[player_status_update.player_id] = player_status_update.status
    return {"message": f"Estado del jugador {player_status_update.player_id} cambiado a {player_status_update.status}"}

