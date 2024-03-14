from enum import Enum


class ResponseStatusMsg(Enum):
    SUCCESS = "Success"
    FAIL = "Fail"


class ResponseMsg(Enum):
    INTERNAL_ERROR = "Internal server error"
    BAD_REQUEST = "Bad request"
    NOT_FOUND = "Data not found"


class LogMsg(Enum):
    # info msg
    ACCEPT_REQ = "Accepting request"
    COMPLETE_REQ = "Request complete"

    # complete msg
    SUCCESS_RESP = "Success"
    INTERNAL_ERR_RESP = "Internal error"
    EXTERNAL_ERR_RESP = "External error"


class ExcludeAuthMiddlewarePath(Enum):
    DOCS = "/docs"
    LOGIN = "/login"
    REGISTER = "/register"
