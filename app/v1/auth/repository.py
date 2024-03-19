from sqlalchemy import text
from sqlalchemy.engine.row import Row

from app.db import Database
from app.db.models.user_mgmt import Platform_Users
from app.helpers.logger import logger
from app.v1.auth.dto import RegisterRequest


class AuthRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def get_user_by_username(self, username: str) -> Row | None:
        """Get user object from given username"""
        user = None

        query = text(
            """
            SELECT
                p.id,
                p.hash_id,
                p.username,
                p.pass_hash,
                p.email
            FROM platform_users AS p
            WHERE p.username = :name
                AND p.is_active = 1
        """
        )
        with self.db.engine.connect() as db_conn:
            user = db_conn.execute(query, {"name": username}).fetchone()

        return user

    def get_user_with_similar_username(self, username: str) -> str | None:
        """Get platform_users object by given username case insensitive"""
        user = None

        query = text(
            """
            SELECT platform_users.username
            FROM platform_users
            WHERE LOWER(platform_users.username) = LOWER(:name)
                AND platform_users.is_active = 1
        """
        )
        with self.db.engine.connect() as db_conn:
            result = db_conn.execute(query, {"name": username}).fetchone()

        if result:
            user = result.username

        return user

    def create_new_user(self, user: RegisterRequest) -> Platform_Users | None:
        """Create new platform_users object"""
        with self.db.session() as db_sess:
            new_user: Platform_Users | None = Platform_Users(**{
                "username": user.username,
                "email": user.email,
                "pass_hash": user.password,
            })
            db_sess.add(new_user)
            try:
                db_sess.commit()
                db_sess.refresh(new_user)
            except Exception as err:
                db_sess.rollback()
                logger.error(f"Fail to add user {user.username}: {err}")
                new_user = None

        return new_user
