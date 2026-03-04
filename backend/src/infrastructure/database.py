from typing import List
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from domain.entities import User, Event, FormatRuleset

SQLALCHEMY_DATABASE_URL = "sqlite:///./rule0.db"
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
