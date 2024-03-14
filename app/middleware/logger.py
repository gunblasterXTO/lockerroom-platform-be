from fastapi import Request, Response

from app.core.constants import LogMsg
from app.helpers.logger import CustomLogger


class LogMiddleware:
    def __init__(self, logger: CustomLogger) -> None:
        self.logger = logger

    async def record_req(self, request: Request) -> None:
        """
        Record incoming request from client.

        Args:
            - request: request body from client-side
        """
        try:
            payload = await request.json()
        except Exception:
            payload = None

        self.logger.accept(
            url=request.url.path,
            method=request.method,
            header=str(request.headers),
            query_param=str(request.query_params),
            payload=payload,
        )

    def record_resp(self, response: Response, time: float) -> None:
        """
        Record response to client.

        Args:
            - response: response object that will be received by client
            - time: time taken until process is completed
        """
        result = ""
        if 200 <= response.status_code < 300:
            result = LogMsg.COMPLETE_REQ.value
        elif 400 <= response.status_code < 500:
            result = LogMsg.EXTERNAL_ERR_RESP.value
        elif 500 >= response.status_code:
            result = LogMsg.INTERNAL_ERR_RESP.value

        self.logger.complete(result, time)
