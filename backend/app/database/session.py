import os
from pathlib import Path
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import declarative_base, sessionmaker

# Configurable database path: anchors to backend/planetpulse.db portably across environments
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB_FILE = BASE_DIR / "planetpulse.db"
DEFAULT_DB_URL = f"sqlite:///{DEFAULT_DB_FILE.as_posix()}"

DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB_URL)
if DATABASE_URL in ("sqlite:///./planetpulse.db", "sqlite:///planetpulse.db"):
    DATABASE_URL = DEFAULT_DB_URL

# For SQLite, check_same_thread is set to False to permit FastAPI multi-threaded request workers,
# and timeout is set to 20 seconds to prevent database locking timeouts under concurrent requests.
connect_args = (
    {"check_same_thread": False, "timeout": 20}
    if DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
)

if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA busy_timeout = 20000;")
            cursor.execute("PRAGMA journal_mode = WAL;")
            cursor.execute("PRAGMA synchronous = NORMAL;")
        except Exception:
            pass
        finally:
            cursor.close()


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
