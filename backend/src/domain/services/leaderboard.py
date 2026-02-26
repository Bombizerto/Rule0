from infrastructure.database import fake_events_db, fake_rulesets_db

def calculate_leaderboard(event_id: str):
    event=next((e for e in fake_events_db if e.id == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
        
    ruleset=next((r for r in fake_rulesets_db if r.id == event.ruleset_id), None)
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
            # Si hay un ganador
            if pod.is_draw:
                for pid in pod.players_ids:
                    scores[pid]+=ruleset.draw_points
            elif pod.winner_id:
                scores[pod.winner_id]+=ruleset.win_points
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

    
    