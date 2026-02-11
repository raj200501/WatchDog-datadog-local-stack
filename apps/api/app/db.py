from contextlib import contextmanager
from pathlib import Path
from sqlmodel import Session, SQLModel, create_engine

from .config import get_settings


settings = get_settings()
engine = create_engine(settings.database_url, echo=False)


def init_db() -> None:
    if settings.database_url.startswith("sqlite:///./"):
        Path("./data").mkdir(parents=True, exist_ok=True)
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session():
    with Session(engine) as session:
        yield session
