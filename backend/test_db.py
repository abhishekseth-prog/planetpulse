"""Database connection test script for SQLite."""

from sqlalchemy import text
from app.database.session import engine, init_db


def test_db_connection():
    """Verify SQLite database connection and query execution."""
    init_db()
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1;")).scalar()
        assert result == 1


if __name__ == "__main__":
    init_db()
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1;")).scalar()
        assert result == 1
        print("SQLite connection successful!")