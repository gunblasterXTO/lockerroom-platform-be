from app.db.models.user_mgmt import Platform_Users

SIMILAR_USERNAME = [
    ("superuser", "superuser"),  # exist
    ("normaluser", None),  # not exist
]
CREATE_USER = [
    ("normaluser", "normal@user.com", "ABC12345", Platform_Users),
]
SUCCESS_GET_USER_BY_USERNAME = [
    ("superuser", "super@user.com", 1, "4f0fa05a8ff04892833fe56e7316ce30")
]
FAIL_GET_USER_BY_USERNAME = [("normaluser", None)]
