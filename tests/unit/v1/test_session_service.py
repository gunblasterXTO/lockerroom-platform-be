import pytest

from sqlalchemy import text

from app.db import db
from app.helpers.exceptions import ConflictClientRequest
from app.v1.session import SessionRepository, SessionService
from tests.unit.data_session_service import (
    CREATE_SESSION_FAIL,
    CREATE_SESSION_SUCCESS,
    GET_USER_SESSION,
)


def delete_session(user_id):
    with db.engine.connect() as db_conn:
        query = text(
            """
            DELETE FROM sessions
            WHERE sessions.platform_user_id = :user_id
        """
        )
        db_conn.execute(query, {"user_id": user_id})
        db_conn.commit()


class TestSessionSercice:
    @pytest.fixture
    def gen_service(self):
        yield SessionService(SessionRepository(db))

    @pytest.mark.parametrize("user_id, result", GET_USER_SESSION)
    def test_get_user_session(self, gen_service, user_id, result):
        session = gen_service.get_user_session(user_id=user_id)

        assert session == result

    @pytest.mark.parametrize("user_id", CREATE_SESSION_SUCCESS)
    def test_create_session_success(self, gen_service, user_id):
        session_id = gen_service.create_session(user_id)

        assert session_id is not None
        assert isinstance(session_id, str)

        delete_session(user_id)

    @pytest.mark.parametrize("user_id, result", CREATE_SESSION_FAIL)
    def test_create_session_fail(self, gen_service, user_id, result):
        gen_service.create_session(user_id)
        with pytest.raises(ConflictClientRequest) as exc_info:
            gen_service.create_session(user_id)

        assert str(exc_info.value) == result

        delete_session(user_id)
