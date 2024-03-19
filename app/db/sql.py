from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.settings import Settings


class Database:
    def __init__(self) -> None:
        if Settings.DB_DIALECT == "sqlite":
            self.engine = create_engine(
                url=Settings.DB_URL,
                connect_args={"check_same_thread": False},  # sqlite only
            )
        else:
            self.engine = create_engine(url=Settings.DB_URL)
        self.session = sessionmaker(
            autocommit=False, autoflush=True, bind=self.engine
        )
