"""
Database engine and session factory for fClient.
Uses MSSQL when USE_MSSQL=1, else SQLite fallback.
"""
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

try:
    from fClient.db_config import USE_MSSQL, DATABASE_URL
except ImportError:
    USE_MSSQL = False
    DATABASE_URL = "sqlite:///apna_sqlite.db"

_engine = None
_SessionLocal = None
POOL_SIZE = 20
MAX_OVERFLOW = 10


def get_engine():
    """Create or return the database engine."""
    global _engine
    if _engine is None:
        if USE_MSSQL:
            _engine = create_engine(
                DATABASE_URL,
                pool_size=POOL_SIZE,
                max_overflow=MAX_OVERFLOW,
                pool_pre_ping=True,
                echo=False,
            )
        else:
            _engine = create_engine(
                "sqlite:///apna_sqlite.db",
                connect_args={"check_same_thread": False, "timeout": 30},
                echo=False,
            )
    return _engine


def get_session_factory():
    """Return the session maker."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            bind=get_engine(),
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )
    return _SessionLocal


@contextmanager
def get_session_for_project(project_id=None):
    """
    Context manager yielding a SQLAlchemy session.
    When USE_MSSQL, uses shared MSSQL; project_id is for scoping in queries.
    """
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
