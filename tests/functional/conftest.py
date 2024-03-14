"""
Define fixture and other configuration options that are
shared across multiple test files.
"""

import pytest

from fastapi.testclient import TestClient

from app import app


@pytest.fixture(scope="module")
def login_jwt():
    client = TestClient(app)
    login_data = {"username": "superuser", "password": "superpassword"}
    response = client.post(url="/v1/auth/login", json=login_data)
    jwt_token = response.json().get("data", {}).get("access_token")

    def _login_jwt():
        return jwt_token

    yield _login_jwt
