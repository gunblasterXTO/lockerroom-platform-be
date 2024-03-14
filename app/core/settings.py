import os
from pathlib import Path
from typing import Final

from dotenv import load_dotenv


env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    PROJECT_NAME = "Base FastAPI Project"
    VERSION = "0.1.0"

    # log
    DEBUG_LOG_FILE: Final = "app.debug.log"
    INFO_LOG_FILE: Final = "app.info.log"
    ERR_LOG_FILE: Final = "app.err.log"

    # database
    DB_USERNAME: Final = os.getenv("DB_USER")
    DB_PWD: Final = os.getenv("DB_PWD")
    DB_SERVER: Final = os.getenv("DB_SERVER")
    DB_PORT: Final = os.getenv("DB_PORT")
    DB_NAME: Final = os.getenv("DB_NAME")
    DB_URL: Final = "sqlite:///sqlite.db"

    # authentication
    ALGO: Final = os.getenv("ALGORITHM", "")
    SECRET_KEY: Final = os.getenv("SECRET_KEY", "")
    TOKEN_EXP_MINUTES: Final = 30
