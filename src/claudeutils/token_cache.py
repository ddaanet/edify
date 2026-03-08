"""Token cache database management using SQLAlchemy."""

import hashlib
from datetime import UTC, datetime
from pathlib import Path

import platformdirs
from anthropic import Anthropic
from sqlalchemy import Integer, String, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from claudeutils.exceptions import FileReadError
from claudeutils.tokens import ModelId, count_tokens_for_file


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""


class TokenCacheEntry(Base):
    """Cached token count keyed by (md5_hex, model_id)."""

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

    Pass ":memory:" for in-memory.
    """
    engine = create_engine(
        f"sqlite:///{db_path}" if db_path != ":memory:" else "sqlite:///:memory:"
    )
    Base.metadata.create_all(engine)
    return engine


def cached_count_tokens_for_file(
    path: Path,
    model: ModelId,
    client: Anthropic,
    cache: TokenCache,
) -> int:
    """Count tokens via cache; falls back to API on miss and stores result."""
    try:
        content = path.read_text()
    except (PermissionError, OSError, UnicodeDecodeError) as e:
        raise FileReadError(str(path), str(e)) from e
    md5_hex = hashlib.md5(content.encode()).hexdigest()  # noqa: S324

    cached = cache.get(md5_hex, model)
    if cached is not None:
        return cached

    count = count_tokens_for_file(path, model, client)
    cache.put(md5_hex, model, count)
    return count


def get_default_cache() -> TokenCache:
    """Create TokenCache at the default platform cache location."""
    cache_dir = Path(platformdirs.user_cache_dir("claudeutils"))
    cache_dir.mkdir(parents=True, exist_ok=True)
    db_path = str(cache_dir / "token_cache.db")
    engine = create_cache_engine(db_path)
    return TokenCache(engine)
