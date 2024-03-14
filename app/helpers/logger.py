import logging
import uuid
from logging.handlers import RotatingFileHandler
from typing import Final

from app.core.constants import LogMsg
from app.core.settings import Settings


class CustomLogger:
    FORMAT: Final = "%(asctime)s - %(levelname)s - %(message)s"
    DATEFMT: Final = "%d-%m-%Y %I:%M:%S"
    MAX_SIZE: Final = 10_000_000  # 10 MB
    BACKUP_COUNT: Final = 5

    def __init__(self) -> None:
        self.uuid: str | None = None
        self._setup_log()

    def _setup_log(self) -> None:
        """Setup log handler, formatter, level, etc."""
        formatter = logging.Formatter(
            fmt=CustomLogger.FORMAT, datefmt=CustomLogger.DATEFMT
        )

        # debug log: log process
        self._debug_logger = logging.getLogger("debug_log")
        self._debug_logger.setLevel(logging.DEBUG)
        debug_file_handler = RotatingFileHandler(
            filename=Settings.DEBUG_LOG_FILE,
            maxBytes=CustomLogger.MAX_SIZE,
            backupCount=CustomLogger.BACKUP_COUNT,
        )
        debug_file_handler.setFormatter(formatter)
        self._debug_logger.addHandler(debug_file_handler)

        # info log: log incoming request and response
        self._info_logger = logging.getLogger("info_log")
        self._info_logger.setLevel(logging.INFO)
        info_file_handler = RotatingFileHandler(
            filename=Settings.INFO_LOG_FILE,
            maxBytes=CustomLogger.MAX_SIZE,
            backupCount=CustomLogger.BACKUP_COUNT,
        )
        info_file_handler.setFormatter(formatter)
        self._info_logger.addHandler(info_file_handler)

        # error log: log error in the process
        self._err_logger = logging.getLogger("err_log")
        self._err_logger.setLevel(logging.ERROR)
        err_file_handler = RotatingFileHandler(
            filename=Settings.ERR_LOG_FILE,
            maxBytes=CustomLogger.MAX_SIZE,
            backupCount=CustomLogger.BACKUP_COUNT,
        )
        err_file_handler.setFormatter(formatter)
        self._err_logger.addHandler(err_file_handler)

    @staticmethod
    def _generate_uuid() -> str:
        """UUID as per request identifier."""
        return str(uuid.uuid4())

    def accept(
        self,
        url: str,
        method: str,
        header: str,
        query_param: str | None = None,
        payload: dict | None = None,
    ) -> None:
        """Record incoming request from client.

        Args:
            - url: full url path used in the request
            - method: HTTP method
            - query_param: query within the url if any
            - payload: body request if any
        """
        self.uuid = self._generate_uuid()
        accept_log = {
            "message": LogMsg.ACCEPT_REQ.value,
            "req_id": self.uuid,
            "url": url,
            "header": header,
            "method": method,
            "query_param": query_param,
            "payload": payload,
        }
        self._info_logger.info(accept_log)

    def complete(self, result: str, time: float) -> None:
        """Record response from server.

        Args:
            - result
            - time: time needed from accepting request until process finish
        """
        complete_log = {"message": result, "req_id": self.uuid, "time": time}
        self._info_logger.info(complete_log)

    def _free_text_log(self, msg: str) -> str:
        """Log message generator as a one source format

        Args:
            - msg: free text log message
        """
        return f"[{self.uuid}] {msg}"

    def debug(self, msg: str) -> None:
        """Record log in debug level

        Args:
            - msg: free text log message
        """
        self._debug_logger.debug(self._free_text_log(msg))

    def error(self, msg: str) -> None:
        """Record log in error level

        Args:
            - msg: free text log message
        """
        self._err_logger.error(self._free_text_log(msg))


logger = CustomLogger()
