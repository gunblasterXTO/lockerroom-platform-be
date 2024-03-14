from fastapi import HTTPException, status


internal_exception = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal error"
)

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

session_expired_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Session has expired",
    headers={"WWW-Authenticate": "Bearer"},
)

uname_pwd_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect username or password",
    headers={"WWW-Authenticate": "Bearer"},
)

registration_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT, detail="User is already registered"
)

session_exist_exception = HTTPException(
    status_code=status.HTTP_409_CONFLICT, detail="User has an active session"
)
