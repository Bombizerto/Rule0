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
    
    players=[user for user in fake_users_db if user.id in event.players and event.player_status.get(user.id, PlayerStatus.ACTIVE) == PlayerStatus.ACTIVE]
    
    if len(players)<3:
        raise HTTPException(status_code=400, detail="No hay suficientes jugadores para generar una ronda")
        
    # Obtener Leaderboard para los puntos de emparejamiento
    try:
        leaderboard_data = calculate_leaderboard(event_id)
        player_scores = {pid: points for pid, points in leaderboard_data}
    except HTTPException:
        player_scores = {pid: 0 for pid in event.players} # Por si falla o es la 1a ronda
        
    # Recopilar Historial de partidas previas para evitar repeticiones
    player_history = {pid: [] for pid in event.players}
    for r in event.rounds:
        for pod in r.pods:
            for pid in pod.players_ids:
                if pid in player_history:
                    player_history[pid].extend([opp for opp in pod.players_ids if opp != pid])
                    
    new_round=create_round(event_id, event.round_number+1, players, player_scores, player_history)
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
        
    enriched_players = []
    for pid in event.players:
        user = next((u for u in fake_users_db if u.id == pid), None)
        status = event.player_status.get(pid, PlayerStatus.ACTIVE).value
        enriched_players.append({
            "id": pid,
            "alias": user.alias if user else "Desconocido",
            "status": status
        })
        
    return {
        "id": event.id,
        "title": event.title,
        "organizer_id": event.organizer_id,
        "ruleset_id": event.ruleset_id,
        "status": event.status,
        "join_code": event.join_code,
        "created_at": event.created_at,
        "players": enriched_players,
        "rounds": event.rounds
    }

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

@router.get("/events/{event_id}/leaderboard")
def get_leaderboard(event_id: str):
    # 1. Obtienes los datos puros (Dominio)
    leaderboard_tuples = calculate_leaderboard(event_id)
    
    # 2. Creamos la lista para los objetos híbridos
    final_leaderboard = []
    
    for player_id, points in leaderboard_tuples:
        # Busca el usuario en fake_users_db usando su ID
        user = next((u for u in fake_users_db if u.id == player_id), None)
        
        # 3. Aquí es donde ocurre la "hibridación"
        # Añade a final_leaderboard un diccionario que tenga:
        # "player_id", "alias" (del usuario) y "points"
        final_leaderboard.append({
            "player_id": player_id,
            "alias": user.alias if user else "Desconocido",
            "points": points
        })
        
    return final_leaderboard

@router.post("/events/{event_id}/close-round")
def close_active_round(event_id: str):
    # 1. Buscamos el Torneo (Evento)
    event = next((e for e in fake_events_db if e.id == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado.")
    # 2. Buscamos la única ronda activa
    active_round = next((r for r in event.rounds if r.is_active), None)
    if not active_round:
        raise HTTPException(status_code=400, detail="No hay ninguna ronda activa para cerrar.")
    # 3. Cerramos el chiringuito
    active_round.is_active = False
    # (Opcional) Aquí iría el reparto de puntos:
    # Si quisieras, podrías coger 'event.standings' y sumar
    # +3 al ganador o +1 a todos al empatar.
    # Transformamos el dataclass a diccionario usando asdict
    from dataclasses import asdict
    return {"message": f"Ronda {active_round.round_number} cerrada con éxito.", "round": asdict(active_round)}


@router.post("/events/{event_id}/close-event")
def close_event(event_id: str):
    # 1. Buscamos el Torneo (Evento)
    event = next((e for e in fake_events_db if e.id == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado.")
    
    # 2. Comprobamos si hay rondas activas colgando
    active_round = next((r for r in event.rounds if r.is_active), None)
    if active_round:
        raise HTTPException(status_code=400, detail="No se puede cerrar el evento: hay una ronda activa en curso.")
        
    # 3. Cerramos el evento
    event.status = EventStatus.COMPLETED
    
    return {"message": "El torneo ha finalizado oficialmente.", "status": event.status}
