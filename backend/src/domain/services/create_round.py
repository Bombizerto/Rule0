import uuid
from datetime import datetime
from typing import List
from domain.entities import Round, Pod, User
from domain.services.matchmaking import run_casual_matchmaking

def create_round(event_id: str, round_number: int, players: List[User]) -> Round:
    """
    Orquesta la creación de una nueva ronda para un evento.
    1. Asigna jugadores a mesas (Pods) usando matchmaking.
    2. Crea la entidad Round con los pods generados.
    """
    pods_users = run_casual_matchmaking(players)
    pods: List[Pod] = []
    for i, pod_users in enumerate(pods_users, start=1):
        pod = Pod(
            id=str(uuid.uuid4()),
            table_number=i,
            players_ids=[user.id for user in pod_users]
        )
        pods.append(pod)
    
    new_round = Round(
        id=str(uuid.uuid4()),
        event_id=event_id,
        round_number=round_number,
        pods=pods,
        is_active=True,
        created_at=datetime.now()
    )

    return new_round