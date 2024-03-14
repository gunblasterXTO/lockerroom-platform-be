from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator

from app.core.settings import Settings


class Database:
    def __init__(self) -> None:
        self._engine = create_engine(
            url=Settings.DB_URL, connect_args={"check_same_thread": False}
        )  # connect_args for sqlite only
        self.session = sessionmaker(
            autocommit=False, autoflush=True, bind=self._engine
        )

    def get_session(self) -> Generator:
        try:
            self.db = self.session()
            yield self.db
        finally:
            self.db.close()
