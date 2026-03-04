import sys
import os

# Añadir src al path para poder importar la infraestructura
sys.path.append(os.path.join(os.getcwd(), 'backend', 'src'))

from infrastructure.database import SessionLocal
from infrastructure.repositories import FormatRulesetRepository
from domain.entities import FormatRuleset

def ensure_ruleset():
    db = SessionLocal()
    try:
        repo = FormatRulesetRepository(db)
        
        # Comprobar si ya existe el ruleset hardcodeado en el frontend
        existing = repo.get_by_id("test-ruleset-123")
        
        rs = FormatRuleset(
            id="test-ruleset-123",
            name="Standard Commander",
            win_points=3,
            draw_points=1,
            kill_points=1,
            allows_custom_achievements=True
        )
        
        repo.save(rs)
        print(f"✅ Ruleset 'Standard Commander' (test-ruleset-123) asegurado en la DB.")
        print(f"   Puntos: Win=3, Draw=1")
    except Exception as e:
        print(f"❌ Error al crear el ruleset: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    ensure_ruleset()
