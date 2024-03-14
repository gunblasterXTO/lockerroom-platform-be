# responsible to store DTOs (Data Transfer Object) between client
# and server and internal business logic.
from datetime import datetime
from pydantic import BaseModel, EmailStr


class LoginRequestDTO(BaseModel):
    username: str
    password: str


class LoginResponseDTO(BaseModel):
    access_token: str


class RegisterRequestDTO(BaseModel):
    username: str
    email: EmailStr
    password: str


class RegisterResponseDTO(BaseModel):
    username: str


class TokenDataDTO(BaseModel):
    """JWT standard structure"""

    sub: str  # username
    sub_id: str
    session: str
    exp: datetime | None = None  # expiry of the token
