# db session and table schema for repository interaction purposes
from sqlalchemy.orm import Session  # noqa

from .session import Database

db = Database()
