import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./planetpulse.db")

# For SQLite, check_same_thread is set to False to permit FastAPI multi-threaded request workers
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db(target_engine=None):
    """Create all configured tables in the database with schema alignment."""
    # Ensure models are imported so that Base.metadata has the table definitions
    import app.models  # noqa: F401
    bind_engine = target_engine or engine
    Base.metadata.create_all(bind=bind_engine)

    # Lightweight column migration check for SQLite
    with bind_engine.connect() as conn:
        try:
            result = conn.execute(text("PRAGMA table_info(activities);"))
            columns = [row[1] for row in result.fetchall()]
            if columns and "co2e" not in columns:
                conn.execute(text("ALTER TABLE activities ADD COLUMN co2e FLOAT NOT NULL DEFAULT 0.0;"))
                conn.commit()
            if columns and "user_id" not in columns:
                conn.execute(text("ALTER TABLE activities ADD COLUMN user_id INTEGER DEFAULT NULL;"))
                conn.commit()
        except Exception:
            pass


# Ensure database tables exist upon module initialization
try:
    init_db()
except Exception:
    pass


def get_db():
    """FastAPI dependency for yielding database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
