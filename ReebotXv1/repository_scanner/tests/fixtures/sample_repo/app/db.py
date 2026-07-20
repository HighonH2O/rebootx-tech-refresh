"""Sample db.py for the test fixture — simulates a database connection module."""

import psycopg2
from sqlalchemy import create_engine


DATABASE_URL = "postgresql://user:pass@localhost:5432/mydb"

engine = create_engine(DATABASE_URL)


def get_connection():
    """Get a raw psycopg2 connection."""
    return psycopg2.connect(DATABASE_URL)


def get_engine():
    """Get the SQLAlchemy engine."""
    return engine
