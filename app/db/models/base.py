from datetime import datetime

from sqlalchemy import Column, DateTime, SmallInteger
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import as_declarative


@as_declarative()
class Base:
    is_active = Column(SmallInteger, default=1)  # 1: active, 0: inactive
    create_date = Column(DateTime, default=datetime.now, nullable=False)
    update_date = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )

    # to generate tablename from classname
    @declared_attr
    def __tablename__(cls):  # type: ignore
        return cls.__name__.lower()
