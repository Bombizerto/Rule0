from infrastructure.database import SessionLocal
from infrastructure.repositories import UserRepository, FormatRulesetRepository, EventRepository
from domain.entities import User, Event, FormatRuleset, EventStatus, PlayerStatus, Role
from datetime import datetime
import uuid

def seed_test_data():
    """Puebla la base de datos SQL con datos de prueba básicos."""
    
    db = SessionLocal()
    try:
        user_repo = UserRepository(db)
        ruleset_repo = FormatRulesetRepository(db)
        event_repo = EventRepository(db)
        
        # 1. Crear Usuarios (4 para una mesa perfecta)
        names = ["Aidan", "Bobi", "Lucas", "Dani", "Elena", "Juan", "Maria", "Pedro", "Ana", "Luis", "Carlos", "María", "Juan", "Ana", "Luis", "Carlos", "María", "Juan", "Ana", "Luis","Papu"]
        users_creados = []
        for i, name in enumerate(names):
            user_id = "test-org-123" if i == 0 else str(uuid.uuid4())
            role_val = Role.ADMIN if i == 0 else Role.PLAYER
            u = User(id=user_id, alias=name, email=f"{name.lower()}@rule0.com", role=role_val, password="password")
            user_repo.save(u)
            users_creados.append(u)

        # 2. Crear Ruleset
        rs = FormatRuleset(
            id="test-ruleset-123",
            name="Casual Commander",
            win_points=3,
            draw_points=1,
            kill_points=1,
            allows_custom_achievements=True
        )
        ruleset_repo.save(rs)

        # 3. Crear Evento
        ev = Event(
            id="test-event-123", # ID fijo para facilitar las pruebas
            title="Torneo de Prueba Alpha",
            organizer_id=users_creados[0].id,
            ruleset_id=rs.id,
            join_code="MTG99",
            players=[u.id for u in users_creados], # Todos inscritos
            status=EventStatus.ACTIVE,
            created_at=datetime.now(),
            player_status={u.id: PlayerStatus.ACTIVE for u in users_creados}
        )
        event_repo.save(ev)
        
        print(f"✅ DB Seeded: {len(users_creados)} usuarios, 1 evento (ID: test-event-123)")
    finally:
        db.close()
