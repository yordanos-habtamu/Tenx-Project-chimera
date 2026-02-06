from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..config.settings import settings

# Database URL from centralized configuration
DATABASE_URL = settings.database_url

# Handle SQLite specific configuration
connect_args = {}
if "sqlite" in DATABASE_URL:
    connect_args = {"check_same_thread": False}
    # SQLite doesn't support pool_size/overflow in the same way with create_engine defaults usually
    engine = create_engine(
        DATABASE_URL, connect_args=connect_args, echo=settings.database_echo
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_pool_overflow,
        echo=settings.database_echo,
    )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db():
    """
    Context manager for database sessions.
    Ensures proper cleanup of database connections.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize the database tables based on models.
    This should be called when setting up the application.
    """
    from .models import Base

    Base.metadata.create_all(bind=engine)


def get_engine():
    """
    Get the database engine instance.
    Useful for advanced database operations.
    """
    return engine
