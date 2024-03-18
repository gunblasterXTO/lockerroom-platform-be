from sqlalchemy import text
from sqlalchemy.engine.row import Row

from app.db import Database
from app.db.models.user_mgmt import Sessions
from app.helpers.logger import logger


class SessionRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def get_session_by_user_id(self, user_id: str) -> Row | None:
        """Get active session by given user hash id"""
        session = None

        query = text(
            """
            SELECT *
            FROM sessions AS s
            WHERE s.platform_user_id = :user_id
                AND s.is_active = 1
        """
        )
        with self.db.engine.connect() as db_conn:
            session = db_conn.execute(query, {"user_id": user_id}).fetchone()

        return session

    def get_session_by_session_id(self, session_id: str) -> Row | None:
        """Get active session by given session id"""
        session = None

        query = text(
            """
            SELECT *
            FROM sessions AS s
            WHERE s.id = :sess_id
                AND s.is_active = 1
        """
        )
        with self.db.engine.connect() as db_conn:
            session = db_conn.execute(
                query, {"sess_id": session_id}
            ).fetchone()

        return session

    def create_new_session(self, user_id: str) -> Sessions | None:
        """Create new session for user"""
        with self.db.session() as db_sess:
            new_session: Sessions | None = Sessions(**{
                "platform_user_id": user_id
            })
            db_sess.add(new_session)
            try:
                db_sess.commit()
                db_sess.refresh(new_session)
            except Exception as exc:
                db_sess.rollback()
                logger.error(f"Fail to create session {user_id}: {exc}")
                new_session

        return new_session

    def set_as_inactive(self, session_id: str) -> bool:
        """Set session is_active to 0"""
        with self.db.session() as db_sess:
            db_sess.query(Sessions).filter(Sessions.id == session_id).update({
                Sessions.is_active: 0
            })
            try:
                db_sess.commit()
                is_inactivated = True
            except Exception as exc:
                db_sess.rollback()
                logger.error(
                    f"Fail to set session as inactive [{session_id}]: {exc}"
                )
                is_inactivated = False

        return is_inactivated
