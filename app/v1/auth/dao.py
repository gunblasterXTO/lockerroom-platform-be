# responsible for handling user input, business flow,
# intermediary between view and the business logic (service).
# stateless, handle particular request and not retain state between request.
from typing import List, Optional, Union

from app.db import Session
from app.db.models.user_mgmt import Sessions, Users
from app.helpers.logger import logger
from app.v1.auth.dto import RegisterRequestDTO


class UserDAO:
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_user_by_username(
        username: str, db_sess: Session
    ) -> Optional[Users]:
        """
        Get user data from username.

        Args:
            - username: user's username from client request
            - db_sess: database session dependency

        Return:
            - user_obj: user object if any
        """
        user = db_sess.query(Users).filter(Users.username == username).first()
        return user

    @staticmethod
    def create_new_user(
        new_user: RegisterRequestDTO, db_sess: Session
    ) -> Optional[Users]:
        """
        Create new user record.

        Args:
            - new_user:  user detail from client request
            - db_sess: database session dependency

        Return:
            - user_obj: newly created user record containing necessary detail
        """
        new_user_dict = {
            "username": new_user.username,
            "email": new_user.email,
            "pass_hash": new_user.password,
        }
        new_user_obj = Users(**new_user_dict)
        db_sess.add(new_user_obj)

        try:
            db_sess.commit()
            user_obj = new_user_obj
        except Exception as err:
            db_sess.rollback()
            logger.error(f"Fail to add user {new_user.username}: {err}")
            user_obj = None

        return user_obj


class SessionDAO:
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_session(
        id: str, username: str, db_sess: Session
    ) -> Optional[Sessions]:
        """
        Get session record.

        Args:
            - id: session id
            - username

        Return:
            - session
        """
        session = (
            db_sess.query(Sessions)
            .filter(Sessions.id == id, Sessions.username == username)
            .first()
        )

        return session

    @staticmethod
    def get_session_by_id(id: str, db_sess: Session) -> Optional[Sessions]:
        """
        Get session record.

        Args:
            - id: session id

        Return:
            - session
        """
        session = db_sess.query(Sessions).filter(Sessions.id == id).first()

        return session

    @staticmethod
    def get_session_by_username(
        username: str, db_sess: Session
    ) -> List[Sessions]:
        """
        Get session record.

        Args:
            - username
            - db_sess

        Return:
            - session
        """
        session = (
            db_sess.query(Sessions)
            .filter(Sessions.username == username, Sessions.is_active == 1)
            .all()
        )

        return session

    @staticmethod
    def create_new_session(
        username: str, db_sess: Session
    ) -> Optional[Sessions]:
        """
        Create new session record.

        Args:
            - user_id
            - session_token
            - exp: token expiry date

        Return:
            - session_id
        """
        new_session_obj = Sessions(**{"username": username})
        db_sess.add(new_session_obj)

        try:
            db_sess.commit()
            session_obj = new_session_obj
        except Exception as err:
            db_sess.rollback()
            logger.error(f"Fail to add session for user {username}: {err}")
            session_obj = None

        return session_obj

    @staticmethod
    def set_as_inactive(
        session_objs: Union[Sessions, List[Sessions]], db_sess: Session
    ) -> bool:
        """
        Set session status to inactive.

        Args:
            - id: session_ id or list of session_id
            - db_sess

        Return:
            boolean
        """
        if isinstance(session_objs, list):
            for session_obj in session_objs:
                session_obj.is_active = 0  # type: ignore
        else:
            session_objs.is_active = 0  # type: ignore

        try:
            db_sess.commit()
        except Exception as err:
            db_sess.rollback()
            logger.error(f"Fail to inactive session {session_objs}: {err}")
            return False
        else:
            return True
