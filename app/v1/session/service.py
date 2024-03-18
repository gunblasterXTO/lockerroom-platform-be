from sqlalchemy.engine.row import Row

from app.helpers.exceptions import ConflictClientRequest, InternalServerError
from app.v1.session.const import SessionErrorMsg
from app.v1.session.repository import SessionRepository


class SessionService:
    def __init__(self, sess_repo: SessionRepository) -> None:
        self.sess_repo = sess_repo

    def get_user_session(
        self, sess_id: str | None = None, user_id: str | None = None
    ) -> Row | None:
        """Get user session by session id or user id"""
        if user_id:
            return self.sess_repo.get_session_by_user_id(user_id)
        elif sess_id:
            return self.sess_repo.get_session_by_session_id(sess_id)

        raise NotImplementedError()

    def create_session(self, user_id: str) -> str:
        """Create new session for a user"""
        if self.sess_repo.get_session_by_user_id(user_id):
            raise ConflictClientRequest(SessionErrorMsg.EXIST_SESSION)

        session = self.sess_repo.create_new_session(user_id)
        if not session:
            raise InternalServerError()

        return str(session.id)

    def blacklist_session(self, session_id: str) -> bool:
        """Ensure session cannot be used after logout or expires"""
        return self.sess_repo.set_as_inactive(session_id)
