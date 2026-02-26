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

if __name__ == "__main__":
    # 1. Simulamos 10 jugadores (esto debería crear 1 mesa de 4 y 2 de 3, según tu algoritmo)
    test_players = [
        User(id=f"u{i}", alias=f"Jugador {i}") for i in range(1, 11)
    ]
    
    # 2. Ejecutamos nuestra creación de ronda
    mi_ronda = create_round(
        event_id="torneo-premium-001",
        round_number=1,
        players=test_players
    )
    
    # 3. Verificamos los resultados por consola
    print(f"\n🚀 {mi_ronda.id}")
    print(f"📅 Creada el: {mi_ronda.created_at}")
    print(f"🔢 Ronda: {mi_ronda.round_number} | Evento: {mi_ronda.event_id}\n")
    
    for pod in mi_ronda.pods:
        print(f"🪑 Mesa {pod.table_number:>2} | Jugadores: {pod.players_ids}")