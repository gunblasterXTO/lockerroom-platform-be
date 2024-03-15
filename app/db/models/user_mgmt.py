from sqlalchemy import Column, ForeignKey, Integer, String

from app.db.models.base import Base
from app.db.models.util import ModelsUtil


class Platform_Users(Base):
    id = Column(Integer, primary_key=True, index=True)
    hash_id = Column(
        String(256), nullable=False, default=ModelsUtil.generate_hash
    )
    username = Column(String(128), nullable=False, unique=True)
    email = Column(String(128), nullable=False, unique=True)
    pass_hash = Column(String(128), nullable=False)


class Sessions(Base):
    id = Column(
        String(64),
        primary_key=True,
        nullable=False,
        index=True,
        default=ModelsUtil.generate_hash,
    )
    username = Column(
        String(256), ForeignKey("platform_users.username"), nullable=False
    )
