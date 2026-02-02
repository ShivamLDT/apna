"""
Database engine and session factory for SQLAlchemy ORM.
Supports MSSQL (when USE_MSSQL) and SQLite fallback.
"""
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from FlaskWebProject3.db_config import (
    USE_MSSQL,
    DATABASE_URL,
    POOL_SIZE,
    MAX_OVERFLOW,
)
from FlaskWebProject3.models import Base

_engine = None
_SessionLocal = None


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
            # SQLite fallback - used for backward compat during migration
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
        engine = get_engine()
        _SessionLocal = sessionmaker(
            bind=engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )
    return _SessionLocal


@contextmanager
def get_session_for_project(project_id=None):
    """
    Context manager yielding a SQLAlchemy session.
    project_id is not auto-injected; callers must filter by project_id in queries.
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


def get_engine_for_app(app):
    """Initialize engine with app context (for Flask-SQLAlchemy style init)."""
    return get_engine()


def create_all_tables():
    """Create all tables in the database."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


def drop_all_tables():
    """Drop all tables (use with caution)."""
    engine = get_engine()
    Base.metadata.drop_all(bind=engine)
