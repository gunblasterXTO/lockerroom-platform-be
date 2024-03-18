from datetime import datetime
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class RegisterResponse(BaseModel):
    username: str
    email: str


class TokenData(BaseModel):
    """JWT standard structure"""

    sub: str  # username
    sub_id: str
    session: str
    exp: datetime | None = None  # expiry of the token
