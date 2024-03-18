import os
from pathlib import Path
from typing import Final

from dotenv import load_dotenv


env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    PROJECT_NAME = "lockerroom platform"
    VERSION = "0.1.0"

    # log
    DEBUG_LOG_FILE: Final = "app.debug.log"
    INFO_LOG_FILE: Final = "app.info.log"
    ERR_LOG_FILE: Final = "app.err.log"

    # database
    DB_DIALECT: Final = os.getenv("DB_DIALECT", "")
    DB_URL: Final = os.getenv(f"DB_{DB_DIALECT}_URL", "")

    # authentication
    ALGO: Final = os.getenv("ALGORITHM", "")
    SECRET_KEY: Final = os.getenv("SECRET_KEY", "")
