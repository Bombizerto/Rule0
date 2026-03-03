import pytest
from datetime import datetime, UTC
from domain.services.leaderboard import calculate_leaderboard
from domain.entities import Event, Round, Pod, FormatRuleset, EventStatus
from infrastructure.repositories import EventRepository, FormatRulesetRepository

@pytest.fixture
def setup_leaderboard_data(db_session):
    """Limpia y prepara datos para las pruebas de clasificación."""
    
    # Ruleset: 3 pt win, 1 pt draw
    rs = FormatRuleset(id="rs1", name="Test", win_points=3, draw_points=1, kill_points=0, allows_custom_achievements=False)
    FormatRulesetRepository(db_session).save(rs)
    
    # Event with 4 players
    ev = Event(
        id="ev1", 
        title="Test Event", 
        organizer_id="admin", 
        ruleset_id="rs1", 
        join_code="ABC", 
        players=["P1", "P2", "P3", "P4"],
        status=EventStatus.ACTIVE,
        rounds=[],
        created_at=datetime.now(UTC),
        player_status={}
    )
    
    # Round 1 (Finished): P1 wins
    p1 = Pod(id="pod1", table_number=1, players_ids=["P1", "P2", "P3", "P4"], winner_id="P1", is_draw=False)
    r1 = Round(id="r1", event_id="ev1", round_number=1, pods=[p1], is_active=False, created_at=datetime.now(UTC))
    
    # Round 2 (Finished): Draw
    p2 = Pod(id="pod2", table_number=1, players_ids=["P1", "P2", "P3", "P4"], winner_id=None, is_draw=True)
    r2 = Round(id="r2", event_id="ev1", round_number=2, pods=[p2], is_active=False, created_at=datetime.now(UTC))
    
    ev.rounds = [r1, r2]
    EventRepository(db_session).save(ev)
    return ev


def test_calculate_leaderboard_accrued_points(setup_leaderboard_data, db_session):
    """Verifica que los puntos se acumulan correctamente (Ganador + Empate)."""
    leaderboard = calculate_leaderboard("ev1", EventRepository(db_session), FormatRulesetRepository(db_session))
    
    # Leaderboard es una lista de tuplas [('ID', puntos), ...]
    # P1: 3 (win) + 1 (draw) = 4
    # P2, P3, P4: 0 (win) + 1 (draw) = 1
    
    results = dict(leaderboard)
    assert results["P1"] == 4
    assert results["P2"] == 1
    assert results["P3"] == 1
    assert results["P4"] == 1

def test_calculate_leaderboard_ordering(setup_leaderboard_data, db_session):
    """Verifica que el ranking está ordenado de mayor a menor."""
    leaderboard = calculate_leaderboard("ev1", EventRepository(db_session), FormatRulesetRepository(db_session))
    
    # El primero debe ser P1
    assert leaderboard[0][0] == "P1"
    assert leaderboard[0][1] == 4

def test_calculate_leaderboard_ignore_active_rounds(setup_leaderboard_data, db_session):
    """Verifica que las rondas activas no suman puntos."""
    ev = setup_leaderboard_data
    # Añadimos una ronda activa donde P2 ganaría (pero no debe sumarse)
    p3 = Pod(id="pod3", table_number=1, players_ids=["P1", "P2", "P3", "P4"], winner_id="P2", is_draw=False)
    r3 = Round(id="r3", event_id="ev1", round_number=3, pods=[p3], is_active=True, created_at=datetime.now(UTC))
    ev.rounds.append(r3)
    EventRepository(db_session).save(ev) # guardamos los cambios
    
    leaderboard = calculate_leaderboard("ev1", EventRepository(db_session), FormatRulesetRepository(db_session))
    results = dict(leaderboard)
    assert results["P2"] == 1 # Sigue teniendo 1 del empate anterior, la r3 se ignora
