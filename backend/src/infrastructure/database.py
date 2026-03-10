from typing import List
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from domain.entities import User, Event, FormatRuleset

# Encontramos la raíz del proyecto para que el path sea siempre el mismo
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "rule0.db")

# Intentamos leer la URL de la base de datos de las variables de entorno (Render/Supabase)
# Si no existe, usamos SQLite local.
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

# Fix para Render/SQLAlchemy: Las URLs de Postgres a veces empiezan por postgres:// 
# pero SQLAlchemy requiere postgresql://
if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Argumentos extra para SQLite
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    # Postgres/Supabase pooling config
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        pool_pre_ping=True,       # Verifica la conexión antes de usarla
        pool_size=5,              # Conexiones persistentes en el pool
        max_overflow=10,          # Picos máximos temporales
        pool_recycle=1800         # Refresca conexiones cada 30min
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------------------------------------------
# TODAVÍA MANTENEMOS ESTO HASTA QUE MUEVAMOS TODO A LA DB
# ----------------------------------------------------
fake_users_db: List[User] = []
fake_events_db: List[Event] = []
fake_rulesets_db: List[FormatRuleset] = []
