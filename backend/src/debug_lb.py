from infrastructure.database import fake_users_db, fake_events_db, fake_rulesets_db
from infrastructure.seed import seed_test_data
from domain.services.leaderboard import calculate_leaderboard

def debug_leaderboard():
    seed_test_data()
    print(f"Total usuarios en DB: {len(fake_users_db)}")
    print(f"Evento ID: {fake_events_db[0].id}")
    print(f"Jugadores en el evento: {fake_events_db[0].players}")
    
    lb = calculate_leaderboard("test-event-123")
    print(f"Leaderboard tuples: {lb}")
    
    final = []
    for pid, pts in lb:
        user = next((u for u in fake_users_db if u.id == pid), None)
        final.append({"id": pid, "alias": user.alias if user else "Unknown", "pts": pts})
    
    print(f"Final Hybrid Object: {final}")

if __name__ == "__main__":
    debug_leaderboard()
