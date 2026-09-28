"""Initialize the PostgreSQL schema without dropping existing data."""

from database import initialize_schema


def migrate():
    initialize_schema()


if __name__ == "__main__":
    migrate()
    print("Authentication schema migration completed.")
