import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app import app
from app.db.models.user_mgmt import Users
from app.db.session import Database

client = TestClient(app)
db = Database()


class TestAuthRoutes:
    def test_register_success(self):
        json_body = {
            "username": "test user",
            "email": "test@email.com",
            "password": "testpassword",
        }
        response = client.post(url="/v1/auth/register", json=json_body)
        response_body = response.json()

        assert response.status_code == status.HTTP_201_CREATED

        assert "status" in response_body
        assert response_body["status"] == "Success"

        assert "data" in response_body
        assert isinstance(response_body["data"], dict)
        assert "username" in response_body["data"]
        assert response_body["data"]["username"] == json_body["username"]

        with db.session() as db_sess:
            (
                db_sess.query(Users)
                .filter(Users.username == json_body["username"])
                .delete()
            )
            db_sess.commit()

    def test_register_fail_username(
        self,
    ):
        json_body = {
            "username": "superuser",
            "email": "test@email.com",
            "password": "testpassword",
        }
        response = client.post(url="/v1/auth/register", json=json_body)
        response_body = response.json()

        assert response.status_code == status.HTTP_409_CONFLICT

        assert "detail" in response_body
        assert response_body["detail"] == "User is already registered"

    @pytest.mark.parametrize(
        "email, status_code, details",
        [
            ("test email", 400, "Validation error"),  # plain text
            ("testemail.com", 400, "Validation error"),  # missing @
            ("testemail@", 400, "Validation error"),  # missing domain
            ("@test.com", 400, "Validation error"),  # missing username
            (
                "test..email@email.com",
                400,
                "Validation error",
            ),  # consecutive dots
            (".email@email.com", 400, "Validation error"),  # leading dots
        ],
    )
    def test_register_fail_email(self, email, status_code, details):
        json_body = {
            "username": "test user",
            "email": email,
            "password": "testpassword",
        }
        response = client.post(url="/v1/auth/register", json=json_body)
        response_body = response.json()

        assert response.status_code == status_code

        assert "detail" in response_body
        assert response_body["detail"] == details

    def test_login_success(self):
        json_body = {"username": "superuser", "password": "superpassword"}
        response = client.post(url="/v1/auth/login", json=json_body)
        response_body = response.json()

        assert response.status_code == status.HTTP_200_OK

        assert "status" in response_body
        assert response_body["status"] == "Success"

        assert "data" in response_body

        assert "access_token" in response_body["data"]
        assert isinstance(response_body["data"]["access_token"], str)

    def test_login_fail_by_username(self):
        json_body = {"username": "user", "password": "superpassword"}
        response = client.post(url="/v1/auth/login", json=json_body)
        response_body = response.json()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response_body.get("detail") == "Incorrect username or password"
        assert "WWW-Authenticate" in response.headers
        assert response.headers.get("WWW-Authenticate") == "Bearer"

    def test_login_fail_by_password(self):
        json_body = {"username": "superuser", "password": "password"}
        response = client.post(url="/v1/auth/login", json=json_body)
        response_body = response.json()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response_body.get("detail") == "Incorrect username or password"
        assert "WWW-Authenticate" in response.headers
        assert response.headers.get("WWW-Authenticate") == "Bearer"

    def test_logout_success(self, login_jwt):
        bearer_token = login_jwt()
        headers = {"Authorization": f"Bearer {bearer_token}"}

        response = client.post(url="/v1/auth/logout", headers=headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT
