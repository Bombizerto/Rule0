from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from domain.services.create_round import create_round
from domain.services.leaderboard import calculate_leaderboard
from domain.entities import User, PlayerStatus, EventStatus
from infrastructure.database import get_db
from infrastructure.repositories import EventRepository, UserRepository, FormatRulesetRepository
from application.schemas import EventResponse, PodWinnerReport, PlayerStatusUpdate

router = APIRouter(prefix="/matchmaking", tags=["Matchmaking"])

@router.post("/events/{event_id}/generate-round")
async def generate_round_endpoint(event_id: str, db: Session = Depends(get_db)):
    """
    Endpoint para generar una nueva ronda de forma automática.
    """
    event_repo = EventRepository(db)
    user_repo = UserRepository(db)
    ruleset_repo = FormatRulesetRepository(db)

    event = event_repo.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    players = []
    for pid in event.players:
        if event.player_status.get(pid, PlayerStatus.ACTIVE) == PlayerStatus.ACTIVE:
            u = user_repo.get_by_id(pid)
            if u:
                players.append(u)
    
    if len(players) < 3:
        raise HTTPException(status_code=400, detail="No hay suficientes jugadores para generar una ronda")
        
    # Obtener Leaderboard para los puntos de emparejamiento
    try:
        leaderboard_data = calculate_leaderboard(event_id, event_repo, ruleset_repo)
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
                    
    new_round = create_round(event_id, event.round_number + 1, players, player_scores, player_history)
    event.rounds.append(new_round)
    event.round_number += 1

    event_repo.save(event)

    return {
        "round": new_round,
        "message": f"Generando ronda para el evento {event_id}",
        "status": "pairing"
    }

@router.get("/events/{event_id}", response_model=EventResponse)
def get_event(event_id: str, db: Session = Depends(get_db)):
    event_repo = EventRepository(db)
    user_repo = UserRepository(db)

    event = event_repo.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
        
    enriched_players = []
    for pid in event.players:
        user = user_repo.get_by_id(pid)
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
async def get_active_round(event_id: str, db: Session = Depends(get_db)):
    event_repo = EventRepository(db)
    event = event_repo.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    if not event.rounds:
        raise HTTPException(status_code=400, detail="No hay rondas generadas para este evento")
    
    # Devolvemos la última ronda de la lista
    return event.rounds[-1]

@router.post("/pods/{pod_id}/report-winner", response_model=User)
async def report_winner(pod_id: str, report: PodWinnerReport, db: Session = Depends(get_db)):
    event_repo = EventRepository(db)
    user_repo = UserRepository(db)

    # Buscar el evento al que pertenece este pod.
    event = event_repo.get_pod_by_id(pod_id)
    if not event:
        raise HTTPException(status_code=404, detail="Pod no encontrado")

    pod = None
    for r in event.rounds:
        for p in r.pods:
            if p.id == pod_id:
                pod = p
                break

    if not pod:
        raise HTTPException(status_code=404, detail="Pod no encontrado")
        
    if report.winner_id not in pod.players_ids:
        raise HTTPException(status_code=400, detail="El jugador no pertenece a este pod")

    pod.winner_id = report.winner_id
    
    # Guardamos el evento que propaga los cambios en cascada a rounds y pods
    event_repo.save(event)

    ganador = user_repo.get_by_id(report.winner_id)
    return ganador

@router.post("/pods/{pod_id}/report-draw")
async def report_draw(pod_id: str, db: Session = Depends(get_db)):
    event_repo = EventRepository(db)
    
    event = event_repo.get_pod_by_id(pod_id)
    if not event:
        raise HTTPException(status_code=404, detail="Pod no encontrado")

    pod = None
    for r in event.rounds:
        for p in r.pods:
            if p.id == pod_id:
                pod = p
                break

    if not pod:
        raise HTTPException(status_code=404, detail="Pod no encontrado")
        
    pod.is_draw = True
    event_repo.save(event)

    return {"message": f"Empate reportado para el pod {pod_id}"}


@router.post("/events/{event_id}/change_player_status")
def change_player_status(event_id: str, player_status_update: PlayerStatusUpdate, db: Session = Depends(get_db)):
    event_repo = EventRepository(db)
    event = event_repo.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    if player_status_update.player_id not in event.players:
        raise HTTPException(status_code=404, detail="Jugador no encontrado")
    if event.status != EventStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="El evento no está activo")
    if player_status_update.status not in PlayerStatus:
        raise HTTPException(status_code=400, detail="Estado de jugador no válido")
        
    event.player_status[player_status_update.player_id] = player_status_update.status
    event_repo.save(event)
    return {"message": f"Estado del jugador {player_status_update.player_id} cambiado a {player_status_update.status}"}


@router.get("/events/{event_id}/leaderboard")
def get_leaderboard(event_id: str, db: Session = Depends(get_db)):
    event_repo = EventRepository(db)
    ruleset_repo = FormatRulesetRepository(db)
    user_repo = UserRepository(db)

    # 1. Obtienes los datos puros (Dominio)
    leaderboard_tuples = calculate_leaderboard(event_id, event_repo, ruleset_repo)
    
    # 2. Creamos la lista para los objetos híbridos
    final_leaderboard = []
    
    for player_id, points in leaderboard_tuples:
        # Busca el usuario
        user = user_repo.get_by_id(player_id)
        
        final_leaderboard.append({
            "player_id": player_id,
            "alias": user.alias if user else "Desconocido",
            "points": points
        })
        
    return final_leaderboard


@router.post("/events/{event_id}/close-round")
def close_active_round(event_id: str, db: Session = Depends(get_db)):
    event_repo = EventRepository(db)
    # 1. Buscamos el Torneo (Evento)
    event = event_repo.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado.")
    # 2. Buscamos la única ronda activa
    active_round = next((r for r in event.rounds if r.is_active), None)
    if not active_round:
        raise HTTPException(status_code=400, detail="No hay ninguna ronda activa para cerrar.")
    # 3. Cerramos el chiringuito
    active_round.is_active = False
    
    event_repo.save(event)

    from dataclasses import asdict
    return {"message": f"Ronda {active_round.round_number} cerrada con éxito.", "round": asdict(active_round)}


@router.post("/events/{event_id}/close-event")
def close_event(event_id: str, db: Session = Depends(get_db)):
    event_repo = EventRepository(db)
    # 1. Buscamos el Torneo (Evento)
    event = event_repo.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado.")
    
    # 2. Comprobamos si hay rondas activas colgando
    active_round = next((r for r in event.rounds if r.is_active), None)
    if active_round:
        raise HTTPException(status_code=400, detail="No se puede cerrar el evento: hay una ronda activa en curso.")
        
    # 3. Cerramos el evento
    event.status = EventStatus.COMPLETED
    event_repo.save(event)
    
    return {"message": "El torneo ha finalizado oficialmente.", "status": event.status}
