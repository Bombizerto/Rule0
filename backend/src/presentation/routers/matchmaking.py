from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from domain.services.create_round import create_round
from domain.services.leaderboard import calculate_leaderboard
from domain.entities import User, PlayerStatus, EventStatus
from infrastructure.database import get_db
from infrastructure.repositories import EventRepository, UserRepository, FormatRulesetRepository
from application.schemas import (EventResponse, PodWinnerReport, PlayerStatusUpdate, 
                                 PodProposeResultRequest, PodConfirmResultRequest,
                                 PodRejectResultRequest, PlayerLoginRequest)

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

    # Si el evento estaba en PENDING, lo pasamos a ACTIVE al generar la primera ronda
    if event.status == EventStatus.PENDING:
        event.status = EventStatus.ACTIVE

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

@router.post("/events/login-player")
def login_player(request: PlayerLoginRequest, db: Session = Depends(get_db)):
    """
    Simula un 'login' para jugadores de un evento usando el Join Code y el Alias.
    """
    import uuid
    # Forzar recarga de uvicorn
    print(f"DEBUG LOGIN: join_code={request.join_code}, alias={request.player_alias}")
    event_repo = EventRepository(db)
    user_repo = UserRepository(db)

    event = event_repo.get_by_join_code(request.join_code)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado o código inválido")

    # Localizar al usuario dentro del evento por su alias
    matched_player_id = None
    for pid in event.players:
        user = user_repo.get_by_id(pid)
        if user and user.alias.lower() == request.player_alias.lower():
            matched_player_id = pid
            if user.password and user.password != request.password:
                raise HTTPException(status_code=401, detail="Contraseña incorrecta para el alias proporcionado")
            # Si no tenía pass (legacy), se loguea igual, o podríamos actualizársela
            break
            
    if not matched_player_id:
        # Registrar como jugador nuevo para el evento
        new_player_id = str(uuid.uuid4())
        new_user = User(id=new_player_id, alias=request.player_alias, password=request.password)
        user_repo.save(new_user)
        
        event.players.append(new_player_id)
        event.player_status[new_player_id] = PlayerStatus.ACTIVE
        event_repo.save(event)
        
        matched_player_id = new_player_id

    # Reutilizamos la lógica del endpoint GET /events/{id}
    # para enviar los datos con los players enriquecidos
    enriched_players = []
    for pid in event.players:
        u = user_repo.get_by_id(pid)
        status = event.player_status.get(pid, PlayerStatus.ACTIVE).value
        enriched_players.append({
            "id": pid,
            "alias": u.alias if u else "Desconocido",
            "status": status
        })

    event_data = {
        "id": event.id,
        "title": event.title,
        "organizer_id": event.organizer_id,
        "status": event.status,
        "join_code": event.join_code,
        "players": enriched_players,
        "rounds": event.rounds
    }

    return {
        "message": "Login successful",
        "player_id": matched_player_id,
        "event_data": event_data
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

@router.post("/pods/{pod_id}/propose-result")
async def propose_result(pod_id: str, request: PodProposeResultRequest, db: Session = Depends(get_db)):
    event_repo = EventRepository(db)
    event = event_repo.get_pod_by_id(pod_id)
    if not event: raise HTTPException(status_code=404, detail="Pod no encontrado")
    
    pod = next((p for r in event.rounds for p in r.pods if p.id == pod_id), None)
    if not pod: raise HTTPException(status_code=404, detail="Pod no encontrado")
    if request.player_id not in pod.players_ids: raise HTTPException(status_code=400, detail="Jugador no en la mesa")
    
    if pod.winner_id or pod.is_draw:
        raise HTTPException(status_code=400, detail="La mesa ya está cerrada por un Administrador")

    # Limpiamos disputas previas y confirmaciones
    pod.is_disputed = False
    pod.confirmations = {request.player_id: True} # El que propone confirma por defecto
    pod.proposed_winner_id = request.winner_id
    pod.proposed_is_draw = request.is_draw
    
    # Comprobar si casualmente todos han confirmado ya solos (ej. poda de 1)
    if len(pod.confirmations) >= len(pod.players_ids):
        pod.winner_id = pod.proposed_winner_id
        pod.is_draw = pod.proposed_is_draw

    event_repo.save(event)
    return {"message": "Resultado propuesto. Pendiente de confirmación.", "pod_id": pod_id}

@router.post("/pods/{pod_id}/confirm-result")
async def confirm_result(pod_id: str, request: PodConfirmResultRequest, db: Session = Depends(get_db)):
    event_repo = EventRepository(db)
    event = event_repo.get_pod_by_id(pod_id)
    if not event: raise HTTPException(status_code=404, detail="Pod no encontrado")
    
    pod = next((p for r in event.rounds for p in r.pods if p.id == pod_id), None)
    if not pod: raise HTTPException(status_code=404, detail="Pod no encontrado")
    if request.player_id not in pod.players_ids: raise HTTPException(status_code=400, detail="Jugador no en la mesa")

    if not pod.proposed_winner_id and not pod.proposed_is_draw:
        raise HTTPException(status_code=400, detail="No hay ningún resultado propuesto para confirmar")
        
    pod.confirmations[request.player_id] = True

    # Si todos confirmaron, cerrar mesa
    if len(pod.confirmations) >= len(pod.players_ids):
        pod.winner_id = pod.proposed_winner_id
        pod.is_draw = pod.proposed_is_draw

    event_repo.save(event)
    status_msg = "Mesa cerrada con éxito" if (pod.winner_id or pod.is_draw) else "Confirmación registrada"
    return {"message": status_msg, "pod_id": pod_id}

@router.post("/pods/{pod_id}/reject-result")
async def reject_result(pod_id: str, request: PodRejectResultRequest, db: Session = Depends(get_db)):
    event_repo = EventRepository(db)
    event = event_repo.get_pod_by_id(pod_id)
    if not event: raise HTTPException(status_code=404, detail="Pod no encontrado")
    
    pod = next((p for r in event.rounds for p in r.pods if p.id == pod_id), None)
    if not pod: raise HTTPException(status_code=404, detail="Pod no encontrado")
    if request.player_id not in pod.players_ids: raise HTTPException(status_code=400, detail="Jugador no en la mesa")

    # Si se rechaza, pasamos a estado de disputa
    pod.is_disputed = True
    pod.proposed_winner_id = None
    pod.proposed_is_draw = False
    pod.confirmations = {}
    
    event_repo.save(event)
    return {"message": "Resultado rechazado. Mesa en disputa, avisen al organizador.", "pod_id": pod_id}

from pydantic import BaseModel

class SwapPlayersRequest(BaseModel):
    source_pod_id: str
    target_pod_id: str
    player_id: str
    
@router.put("/pods/swap-players")
def swap_players(request: SwapPlayersRequest, db: Session = Depends(get_db)):
    event_repo = EventRepository(db)
    
    # 1. Obtenemos el evento del pod de origen (técnicamente, fuente y objetivo están en el mismo evento)
    event = event_repo.get_pod_by_id(request.source_pod_id)
    if not event:
        raise HTTPException(status_code=404, detail="Pod Origen u Evento no encontrado")
        
    source_pod = None
    target_pod = None
    
    # Buscamos en la ronda activa de este evento los dos pods
    for r in event.rounds:
        if r.is_active:
            for p in r.pods:
                if p.id == request.source_pod_id:
                    source_pod = p
                if p.id == request.target_pod_id:
                    target_pod = p
            break # si encontramos los pods, no seguimos buscando

    if not source_pod or not target_pod:
        raise HTTPException(status_code=404, detail="Uno o ambos Pods no encontrados en la ronda activa")
        
    if request.player_id not in source_pod.players_ids:
        raise HTTPException(status_code=400, detail="El jugador no está en la mesa de origen")
        
    if len(target_pod.players_ids) >= 4 and source_pod.id != target_pod.id:
         raise HTTPException(status_code=400, detail="La mesa de destino ya está llena")
         
    # Hacemos el SWAP en local
    source_pod.players_ids.remove(request.player_id)
    target_pod.players_ids.append(request.player_id)
    
    event_repo.save(event)
    
    return {"message": "Jugador movido con éxito", "event_id": event.id}

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

@router.post("/events/{event_id}/change_player_status")
def change_player_status(event_id: str, request: PlayerStatusUpdate, db: Session = Depends(get_db)):
    """Endpoint para que el ADMINISTRADOR cambie el estado de cualquier jugador."""
    print(f"DEBUG: admin change status - event={event_id}, player={request.player_id}, status={request.status}")
    try:
        event_repo = EventRepository(db)
        event = event_repo.get_by_id(event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Evento no encontrado.")
        
        if request.player_id not in event.players:
            raise HTTPException(status_code=404, detail="Jugador no inscrito en este evento.")
        
        # El admin tiene poder total, puede cambiar a cualquier estado
        new_st = PlayerStatus(request.status)
        event.player_status[request.player_id] = new_st
        event_repo.save(event)
        
        return {"message": f"Estado del jugador actualizado a {new_st.value}"}
    except Exception as e:
        print(f"DEBUG ERROR: {str(e)}")
        raise e


@router.post("/events/{event_id}/self_change_status")
def self_change_status(event_id: str, request: PlayerStatusUpdate, db: Session = Depends(get_db)):
    """Endpoint para que el PROPIO JUGADOR cambie su estado."""
    event_repo = EventRepository(db)
    event = event_repo.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado.")
    
    if request.player_id not in event.players:
        raise HTTPException(status_code=404, detail="No estás inscrito en este evento.")

    current_status = event.player_status.get(request.player_id)
    new_status = PlayerStatus(request.status)

    # Lógica de protección:
    # 1. Si el jugador está en SELF_DROPPED o DROPPED, no puede reactivarse solo (necesita al admin)
    if current_status in [PlayerStatus.DROPPED, PlayerStatus.SELF_DROPPED] and new_status == PlayerStatus.ACTIVE:
        raise HTTPException(
            status_code=403, 
            detail="Has abandonado el torneo. Debes solicitar al organizador que te reactive manualmente."
        )

    # 2. Si el jugador elige DROPPED, lo marcamos como SELF_DROPPED para que el admin sepa que fue voluntario
    if new_status == PlayerStatus.DROPPED:
        new_status = PlayerStatus.SELF_DROPPED

    # 3. Solo permitimos transiciones lógicas para el jugador: PAUSE/ACTIVE/DROP
    if new_status not in [PlayerStatus.ACTIVE, PlayerStatus.PAUSED, PlayerStatus.SELF_DROPPED]:
         raise HTTPException(status_code=400, detail="Acción no permitida para el jugador.")

    event.player_status[request.player_id] = new_status
    event_repo.save(event)
    
    return {"message": f"Tu estado ha sido actualizado a {new_status.value}"}

