from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, JSON, Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from infrastructure.database import Base
from domain.entities import EventStatus, PlayerStatus, Role
from datetime import datetime

class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    alias = Column(String, index=True)
    password = Column(String, nullable=True)
    email = Column(String, nullable=True)
    is_guest = Column(Boolean, default=False)
    role = Column(SQLEnum(Role), default=Role.PLAYER)
    seat_history = Column(JSON, default=dict)


class FormatRulesetModel(Base):
    __tablename__ = "format_rulesets"

    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    win_points = Column(Integer)
    draw_points = Column(Integer)
    kill_points = Column(Integer)
    allows_custom_achievements = Column(Boolean, default=False)


class EventModel(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    organizer_id = Column(String, index=True)
    ruleset_id = Column(String, ForeignKey("format_rulesets.id"))
    join_code = Column(String, index=True)
    
    # Mapearemos a JSON para simplificar y mantener compatibilidad 1:1 con la estructura lista/diccionario actual
    players = Column(JSON, default=list) 
    player_status = Column(JSON, default=dict)
    
    status = Column(SQLEnum(EventStatus), default=EventStatus.PENDING)
    created_at = Column(DateTime, nullable=True)
    round_number = Column(Integer, default=0)

    # Relación uno-a-muchos con Rounds
    rounds = relationship("RoundModel", back_populates="event", cascade="all, delete-orphan")


class RoundModel(Base):
    __tablename__ = "rounds"

    id = Column(String, primary_key=True, index=True)
    event_id = Column(String, ForeignKey("events.id"))
    round_number = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=True)

    event = relationship("EventModel", back_populates="rounds")
    pods = relationship("PodModel", back_populates="round", cascade="all, delete-orphan")


class PodModel(Base):
    __tablename__ = "pods"

    id = Column(String, primary_key=True, index=True)
    round_id = Column(String, ForeignKey("rounds.id"))
    table_number = Column(Integer)
    
    players_ids = Column(JSON, default=list)
    winner_id = Column(String, nullable=True)
    is_draw = Column(Boolean, default=False)
    
    proposed_winner_id = Column(String, nullable=True)
    proposed_is_draw = Column(Boolean, default=False)
    confirmations = Column(JSON, default=dict)
    is_disputed = Column(Boolean, default=False)

    round = relationship("RoundModel", back_populates="pods")
