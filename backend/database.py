"""
backend/database.py — SQLAlchemy models and DB setup
"""
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/safenet.db")
engine  = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base    = declarative_base()


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


# ── Models ────────────────────────────────────────────────────────────────────

class Parent(Base):
    __tablename__ = "parents"
    id            = Column(Integer, primary_key=True, index=True)
    username      = Column(String(80), unique=True, nullable=False)
    email         = Column(String(120), unique=True, nullable=True)
    hashed_pw     = Column(String(200), nullable=False)
    created_at    = Column(DateTime, default=datetime.utcnow)
    children      = relationship("Child", back_populates="parent")
    notifications = relationship("Notification", back_populates="parent")


class Child(Base):
    __tablename__   = "children"
    id              = Column(Integer, primary_key=True, index=True)
    parent_id       = Column(Integer, ForeignKey("parents.id"))
    name            = Column(String(80), nullable=False)
    link_code       = Column(String(12), unique=True)
    device_id       = Column(String(100), nullable=True)
    is_online       = Column(Boolean, default=False)
    device_locked   = Column(Boolean, default=False)
    internet_paused = Column(Boolean, default=False)
    screen_time_limit = Column(Integer, default=0)       # minutes/day
    created_at      = Column(DateTime, default=datetime.utcnow)
    parent          = relationship("Parent", back_populates="children")
    activity_logs   = relationship("ActivityLog", back_populates="child")
    threat_logs     = relationship("ThreatLog",   back_populates="child")
    screenshots     = relationship("Screenshot",  back_populates="child")


class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id            = Column(Integer, primary_key=True, index=True)
    child_id      = Column(Integer, ForeignKey("children.id"))
    log_type      = Column(String(40))      # website / app / keyboard / search
    value         = Column(Text)
    timestamp     = Column(DateTime, default=datetime.utcnow)
    child         = relationship("Child", back_populates="activity_logs")


class ThreatLog(Base):
    __tablename__  = "threat_logs"
    id             = Column(Integer, primary_key=True, index=True)
    child_id       = Column(Integer, ForeignKey("children.id"))
    threat_type    = Column(String(60))
    confidence     = Column(Float)
    source_text    = Column(Text)
    source         = Column(String(80))      # keyboard / url / screenshot
    action_taken   = Column(String(80))
    timestamp      = Column(DateTime, default=datetime.utcnow)
    child          = relationship("Child", back_populates="threat_logs")


class Screenshot(Base):
    __tablename__ = "screenshots"
    id            = Column(Integer, primary_key=True, index=True)
    child_id      = Column(Integer, ForeignKey("children.id"))
    filename      = Column(String(200))
    reason        = Column(String(200))
    timestamp     = Column(DateTime, default=datetime.utcnow)
    child         = relationship("Child", back_populates="screenshots")


class BlockedWebsite(Base):
    __tablename__ = "blocked_websites"
    id            = Column(Integer, primary_key=True, index=True)
    parent_id     = Column(Integer, ForeignKey("parents.id"))
    child_id      = Column(Integer, ForeignKey("children.id"), nullable=True)
    url           = Column(String(300))
    reason        = Column(String(200), nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow)


class BlockedApplication(Base):
    __tablename__ = "blocked_applications"
    id            = Column(Integer, primary_key=True, index=True)
    parent_id     = Column(Integer, ForeignKey("parents.id"))
    child_id      = Column(Integer, ForeignKey("children.id"), nullable=True)
    app_name      = Column(String(200))
    created_at    = Column(DateTime, default=datetime.utcnow)


class RiskScore(Base):
    __tablename__ = "risk_scores"
    id            = Column(Integer, primary_key=True, index=True)
    child_id      = Column(Integer, ForeignKey("children.id"))
    score         = Column(Float, default=0)
    timestamp     = Column(DateTime, default=datetime.utcnow)


class Notification(Base):
    __tablename__ = "notifications"
    id            = Column(Integer, primary_key=True, index=True)
    parent_id     = Column(Integer, ForeignKey("parents.id"))
    child_id      = Column(Integer, ForeignKey("children.id"))
    message       = Column(Text)
    category      = Column(String(60))
    is_read       = Column(Boolean, default=False)
    timestamp     = Column(DateTime, default=datetime.utcnow)
    parent        = relationship("Parent", back_populates="notifications")


def init_db():
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/screenshots", exist_ok=True)
    Base.metadata.create_all(bind=engine)
