from pathlib import Path
import os
from sqlmodel import SQLModel, Session, create_engine
from app.database import models  # noqa: F401 - register tables

DB_PATH = Path(os.getenv("DATABASE_PATH", str(Path(__file__).resolve().parents[2] / "database.db")))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
engine = create_engine(f"sqlite:///{DB_PATH.as_posix()}", echo=False, connect_args={"check_same_thread": False})

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
