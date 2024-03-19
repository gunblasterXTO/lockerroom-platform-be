import time

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)

from app.helpers.exceptions import (
    InternalServerError,
    UnauthorizedClientRequest,
)
from app.helpers.logger import logger
from app.helpers.response import BaseFailResponse
from app.middleware.logger import LogMiddleware
from app.middleware.monitoring import MonitoringMiddleware
from app.middleware.security import SecurityMiddleware


class Middlewares(BaseHTTPMiddleware):
    LOG = LogMiddleware(logger)
    SECURITY = SecurityMiddleware()
    MONITOR = MonitoringMiddleware()

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Main entry when call this class in fastapi.add_middleware.

        Args:
            - request: client request detail including url, json body, etc.
            - call_next: to call the endpoint/next process
        """
        start_time = time.perf_counter()
        await Middlewares.LOG.record_req(request=request)

        auth_header = request.headers.get("Authorization", "")
        endpoint = request.url.path
        method = request.method

        try:
            sub_id, sub, session_id = Middlewares.SECURITY.authenticate_user(
                auth_header=auth_header, path=endpoint
            )
        except UnauthorizedClientRequest as exc:
            http_status = status.HTTP_401_UNAUTHORIZED
            Middlewares.MONITOR.record_count(endpoint, method, http_status)
            return JSONResponse(
                content=BaseFailResponse(detail=exc.message).model_dump(),
                status_code=http_status,
                headers={"WWW-Authenticate": "Bearer"},
            )
        except InternalServerError as exc:
            http_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            Middlewares.MONITOR.record_count(endpoint, method, http_status)
            return JSONResponse(
                content=BaseFailResponse(detail=exc.message).model_dump(),
                status_code=http_status,
            )

        if any([sub_id, sub, session_id]):
            request.state.session_id = session_id
            request.state.username = sub
            request.state.user_id = sub_id

        response = await call_next(request)
        Middlewares.MONITOR.record_count(
            endpoint, method, response.status_code
        )

        total_time = time.perf_counter() - start_time
        Middlewares.MONITOR.record_histo(method, endpoint, total_time)
        Middlewares.LOG.record_resp(response, total_time)

        return response
