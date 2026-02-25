import pytest
from domain.services.matchmaking import calculate_tables, create_groups, assign_seats
from domain.entities import User

def test_calculate_tables_multiple_of_4():
    """Prueba con números divisibles por 4 (ideal)."""
    assert calculate_tables(12) == (0, 3)
    assert calculate_tables(16) == (0, 4)

def test_calculate_tables_with_remainder():
    """Prueba con restos que requieren mesas de 3."""
    # 9 jugadores: 3 mesas de 3, 0 de 4
    # (En realidad 9-9=0 // 4 = 0) -> (3, 0)
    assert calculate_tables(9) == (3, 0)
    
    # 10 jugadores: 2 mesas de 3, 1 de 4
    # (10-6=4 // 4 = 1) -> (2, 1)
    assert calculate_tables(10) == (2, 1)
    
    # 11 jugadores: 1 mesa de 3, 2 de 4
    # (11-3=8 // 4 = 2) -> (1, 2)
    assert calculate_tables(11) == (1, 2)

def test_calculate_tables_large_number():
    """Prueba con un número grande."""
    assert calculate_tables(100) == (0, 25)

def test_calculate_tables_minimum():
    """Prueba con el mínimo de jugadores (3)."""
    assert calculate_tables(3) == (1, 0)

def test_create_groups_10_players():
    """Prueba que 10 jugadores se reparten en una mesa de 4 y dos de 3."""
    players = [f"P{i}" for i in range(1, 11)]
    groups = create_groups(players)
    
    # Verificamos que el número de mesas es correcto (1 mesa de 4 y 2 mesas de 3)
    # Total de mesas: 3
    assert len(groups) == 3
    
    # El orden puede variar por el shuffle, pero las mesas de 4 van primero según el código
    # Verificamos tamaños de los grupos
    table_sizes = [len(g) for g in groups]
    assert table_sizes[0] == 4
    assert table_sizes[1] == 3
    assert table_sizes[2] == 3
    
    # Verificamos que todos los jugadores originales están presentes
    all_assigned_players = [p for group in groups for p in group]
    assert sorted(all_assigned_players) == sorted(players)

def test_create_groups_randomness():
    """Prueba que los grupos son aleatorios (probabilístico)."""
    players = [f"P{i}" for i in range(1, 11)]
    groups1 = create_groups(players.copy())
    groups2 = create_groups(players.copy())
    
    # Es extremadamente improbable que el shuffle dé el mismo resultado exacto
    assert groups1 != groups2

def test_assign_seats_priority():
    """Prueba que se prioriza a los jugadores con menos historial de asiento 1."""
    u1 = User(id="1", alias="Aidan", seat_history={1: 5, 2: 0, 3: 0, 4: 0})
    u2 = User(id="2", alias="Bobi",  seat_history={1: 2, 2: 0, 3: 0, 4: 0})
    u3 = User(id="3", alias="Lucas", seat_history={1: 0, 2: 0, 3: 0, 4: 0})
    u4 = User(id="4", alias="Dani",  seat_history={1: 0, 2: 0, 3: 0, 4: 0})
    
    mesa = [u1, u2, u3, u4]
    posiciones = assign_seats(mesa)
    
    # Los dos últimos siempre deben ser Bobi (2) y Aidan (5)
    assert posiciones[2].alias == "Bobi"
    assert posiciones[3].alias == "Aidan"
    # Los dos primeros deben tener historial 0
    assert posiciones[0].seat_history[1] == 0
    assert posiciones[1].seat_history[1] == 0

def test_assign_seats_random_tiebreak():
    """Prueba que el desempate es aleatorio (probabilístico)."""
    # Dos jugadores con el mismo historial exactamente
    u1 = User(id="1", alias="Lucas", seat_history={1: 0, 2: 0, 3: 0, 4: 0})
    u2 = User(id="2", alias="Dani",  seat_history={1: 0, 2: 0, 3: 0, 4: 0})
    
    # Ejecutamos varias veces y verificamos que el orden cambia
    results = set()
    for _ in range(20):
        posiciones = assign_seats([u1, u2])
        results.add(tuple(p.alias for p in posiciones))
    
    # Debe haber al menos dos combinaciones distintas: ('Lucas', 'Dani') y ('Dani', 'Lucas')
    assert len(results) > 1
