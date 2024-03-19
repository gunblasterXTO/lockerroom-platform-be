class AuthRule:
    MAX_USERNAME_CHAR = 25
    TOKEN_EXPIRES = 1  # minutes


class RegisterErrorMsg:
    EMPTY_USERNAME = "Username cannot be empty"
    MAX_CHAR_USENAME = (
        f"Username exceed max limit char " f"({AuthRule.MAX_USERNAME_CHAR})"
    )
    NO_ALPHABET_USERNAME = "Username should contain alphabet"
    REGISTERED_USERNAME = "Username is already registered"


class LoginErrorMsg:
    UNAUTHORIZED_USER = "Incorrect username or password"
    OCCUPIED_SESSION = "User already in session"
    EXPIRED_SESSION = "Session has expired"
    INVALID_CREDS = "Could not validate credentials"
