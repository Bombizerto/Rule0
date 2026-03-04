from typing import List
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from domain.entities import User, Event, FormatRuleset

# Encontramos la raíz del proyecto para que el path sea siempre el mismo
# infrastructure/database.py -> infrastructure -> src
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "rule0.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# Para SQLite es importante setear check_same_thread=False en FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
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
