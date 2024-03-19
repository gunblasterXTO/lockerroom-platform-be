from app.v1.auth.dto import LoginResponse, RegisterResponse
from app.v1.auth.const import AuthRule, LoginErrorMsg

TEST_LOGIN_FAIL_CREDS = [
    # wrong username
    ("normaluser", "superpassword", LoginErrorMsg.UNAUTHORIZED_USER),
    # wrong password
    ("superuser", "normalpassword", LoginErrorMsg.UNAUTHORIZED_USER),
    # wrong both usename and password
    ("superuser", "normalpassword", LoginErrorMsg.UNAUTHORIZED_USER),
]
TEST_LOGIN_FAIL_SESSION = [
    # login two times (assuming login from different devices)
    # the first login already happen in test_login_success
    ("superuser", "superpassword", LoginErrorMsg.OCCUPIED_SESSION)
]
TEST_LOGIN_SUCCESS = [
    (
        "superuser",
        "superpassword",
        "bearer",
        AuthRule.TOKEN_EXPIRES,
        LoginResponse,
    )
]

TEST_REGISTER_SUCCESS = [
    ("gunblasterxto", "xto@gmail.com", "123456789", RegisterResponse),
    ("Amburadul123", "amburadul@sial.com", "ambyar", RegisterResponse),
]
TEST_REGISTER_FAIL_USERNAME_DUPS = [
    (
        "superuser",
        "super@user.com",
        "superpassword",
        "Username is already registered",
    ),
    (
        "SUPERUSER",
        "super@user.com",
        "superpassword",
        "Username is already registered",
    ),
    (
        "SuperUser",
        "super@user.com",
        "superpassword",
        "Username is already registered",
    ),
]
TEST_REGISTER_FAIL_USERNAME_REQ = [
    # empty username
    ("", "xto@gmail.com", "123456789", "Username cannot be empty"),
    # username not containing any alphabet
    ("123", "xto@gmail.com", "123456789", "Username should contain alphabet"),
    # username exceed max limit character
    (
        "amburadulgunblasterxtohehe",
        "xto@gmail.com",
        "123456789",
        "Username exceed max limit char (25)",
    ),
]
