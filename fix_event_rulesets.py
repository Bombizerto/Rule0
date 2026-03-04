import sys
import os

# Añadir src al path para poder importar la infraestructura
sys.path.append(os.path.join(os.getcwd(), 'backend', 'src'))

from infrastructure.database import SessionLocal
from infrastructure.repositories import EventRepository, FormatRulesetRepository
from domain.entities import FormatRuleset

def fix_events():
    db = SessionLocal()
    try:
        event_repo = EventRepository(db)
        ruleset_repo = FormatRulesetRepository(db)
        
        # Asegurar que el ruleset existe
        rs = ruleset_repo.get_by_id("test-ruleset-123")
        if not rs:
            print("❌ El ruleset test-ruleset-123 no existe. Abortando.")
            return

        events = event_repo.list_all()
        fixed_count = 0
        for ev in events:
            if not ev.ruleset_id or ev.ruleset_id != "test-ruleset-123":
                print(f"🔧 Arreglando evento '{ev.title}' ({ev.id}): ruleset_id={ev.ruleset_id} -> test-ruleset-123")
                ev.ruleset_id = "test-ruleset-123"
                event_repo.save(ev)
                fixed_count += 1
        
        if fixed_count == 0:
            print("✅ Todos los eventos tienen el ruleset correcto.")
        else:
            print(f"✅ Se han corregido {fixed_count} eventos.")
            
    except Exception as e:
        print(f"❌ Error al arreglar eventos: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_events()
