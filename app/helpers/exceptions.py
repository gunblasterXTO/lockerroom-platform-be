class BadClientReqeust(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ConflictClientRequest(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class UnauthorizedClientRequest(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class InternalServerError(Exception):
    def __init__(self) -> None:
        self.message = "Internal error"
        super().__init__(self.message)
