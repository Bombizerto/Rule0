from fastapi import HTTPException
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from infrastructure.repositories import EventRepository, FormatRulesetRepository

def calculate_leaderboard(event_id: str, event_repo: 'EventRepository', ruleset_repo: 'FormatRulesetRepository'):
    event = event_repo.get_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
        
    ruleset = ruleset_repo.get_by_id(event.ruleset_id)
    if not ruleset:
        raise HTTPException(status_code=404, detail="Formato de reglas no encontrado")
        
    # Diccionario de puntuaciones
    scores={player_id:0 for player_id in event.players}
    
    # Recorremos todas las rondas
    for round in event.rounds:
        if round.is_active:
            continue
        # Recorremos todos los pods
        for pod in round.pods:
            # Si hay un empate
            if pod.is_draw:
                for pid in pod.players_ids:
                    scores[pid]+=ruleset.draw_points
            elif pod.winner_id:
                scores[pod.winner_id]+=ruleset.win_points
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)