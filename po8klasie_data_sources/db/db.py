import contextlib
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session


class DatabaseManager:
    database_url: str
    _engine: Engine = None

    def __init__(self, database_url: str):
        self.database_url = database_url

    def _create_engine(self):
        self._engine = create_engine(self.database_url)

    def get_engine(self):
        if not self._engine:
            self._create_engine()
        return self._engine

    @contextlib.contextmanager
    def session(self) -> Generator[Session, None, None]:
        yield Session(self.get_engine())
