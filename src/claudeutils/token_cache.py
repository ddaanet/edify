"""Token cache database management using SQLAlchemy."""

from datetime import UTC, datetime

from sqlalchemy import Integer, String, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


class TokenCacheEntry(Base):
    """Cached token count entry."""

    __tablename__ = "token_cache"

    md5_hex: Mapped[str] = mapped_column(String, primary_key=True)
    model_id: Mapped[str] = mapped_column(String, primary_key=True)
    token_count: Mapped[int] = mapped_column(Integer)
    last_used: Mapped[datetime] = mapped_column()


class TokenCache:
    """Token count cache backed by SQLite via SQLAlchemy."""

    def __init__(self, engine: Engine) -> None:
        """Initialize cache with database engine."""
        self._session_factory = sessionmaker(bind=engine)

    def get(self, md5_hex: str, model_id: str) -> int | None:
        """Look up cached token count.

        Returns None on miss. Updates last_used on hit.
        """
        with self._session_factory() as session:
            entry = session.get(TokenCacheEntry, (md5_hex, model_id))
            if entry is None:
                return None
            entry.last_used = datetime.now(UTC)
            session.commit()
            return entry.token_count

    def put(self, md5_hex: str, model_id: str, token_count: int) -> None:
        """Store or update token count."""
        with self._session_factory() as session:
            entry = session.get(TokenCacheEntry, (md5_hex, model_id))
            now = datetime.now(UTC)
            if entry is None:
                entry = TokenCacheEntry(
                    md5_hex=md5_hex,
                    model_id=model_id,
                    token_count=token_count,
                    last_used=now,
                )
                session.add(entry)
            else:
                entry.token_count = token_count
                entry.last_used = now
            session.commit()


def create_cache_engine(db_path: str) -> Engine:
    """Create database engine and initialize tables.

    Args:
        db_path: Path to database file (or ":memory:" for in-memory)

    Returns:
        SQLAlchemy Engine instance with tables created
    """
    engine = create_engine(
        f"sqlite:///{db_path}" if db_path != ":memory:" else "sqlite:///:memory:"
    )
    Base.metadata.create_all(engine)
    return engine
