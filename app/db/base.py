# import all the models so Base has them before being
# imported by Alembic
from app.db.models.base import Base  # noqa
from app.db.models.user_mgmt import *  # noqa
