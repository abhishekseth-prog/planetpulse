"""Database connection and session configuration using SQLite."""

from __future__ import annotations

import os
from pathlib import Path
from sqlalchemy import text
from app.database.session import Base, SessionLocal, engine, get_db, init_db

__all__ = ["Base", "SessionLocal", "engine", "get_db", "init_db", "get_connection"]


def get_connection():
    """Return a connection from the configured SQLAlchemy SQLite engine."""
    return engine.connect()
