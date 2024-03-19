import pytest

from sqlalchemy import text

from app.db import db
from app.v1.session.repository import SessionRepository
from tests.unit.data_session_repository import (
    CREATE_SESSION,
    GET_SESSION_BY_USER_ID,
)


class TestSessionRepository:
    @pytest.fixture
    def gen_repo(self):
        yield SessionRepository(db)

    @pytest.mark.parametrize("user_id, result", GET_SESSION_BY_USER_ID)
    def test_get_session_by_user_id(self, gen_repo, user_id, result):
        session = gen_repo.get_session_by_user_id(user_id)

        assert session == result

    @pytest.mark.parametrize("user_id, type", CREATE_SESSION)
    def test_create_new_session(self, gen_repo, user_id, type):
        session = gen_repo.create_new_session(user_id)

        assert isinstance(session, type)
        assert isinstance(session.id, str)
        assert session.platform_user_id == user_id
        assert session.is_active == 1

        with db.engine.connect() as db_conn:
            query = text(
                """
                DELETE FROM sessions
                WHERE sessions.id = :session_id
            """
            )
            db_conn.execute(query, {"session_id": session.id})
            db_conn.commit()
