from infrastructure.database import fake_users_db, fake_events_db, fake_rulesets_db
from domain.entities import User, Event, FormatRuleset, EventStatus, PlayerStatus
from datetime import datetime
import uuid

def seed_test_data():
    """Puebla la base de datos en memoria con datos de prueba básicos."""
    # 1. Limpiar (por si acaso)
    fake_users_db.clear()
    fake_events_db.clear()
    fake_rulesets_db.clear()

    # 2. Crear Usuarios (4 para una mesa perfecta)
    names = ["Aidan", "Bobi", "Lucas", "Dani", "Elena"]
    for name in names:
        u = User(id=str(uuid.uuid4()), alias=name, email=f"{name.lower()}@rule0.com")
        fake_users_db.append(u)

    # 3. Crear Ruleset
    rs = FormatRuleset(
        id=str(uuid.uuid4()),
        name="Casual Commander",
        win_points=3,
        draw_points=1,
        kill_points=1,
        allows_custom_achievements=True
    )
    fake_rulesets_db.append(rs)

    # 4. Crear Evento
    ev = Event(
        id="test-event-123", # ID fijo para facilitar las pruebas en Bruno
        title="Torneo de Prueba Alpha",
        organizer_id=fake_users_db[0].id,
        ruleset_id=rs.id,
        join_code="MTG99",
        players=[u.id for u in fake_users_db], # Todos inscritos
        status=EventStatus.ACTIVE,
        created_at=datetime.now(),
        player_status={u.id: PlayerStatus.ACTIVE for u in fake_users_db}
    )
    fake_events_db.append(ev)
    
    print(f"✅ DB Seeded: {len(fake_users_db)} usuarios, 1 evento (ID: test-event-123)")
