import time

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)

from app.helpers.logger import logger
from app.helpers.response import BaseFailResponse
from app.middleware.logger import LogMiddleware
from app.middleware.security import SecurityMiddleware


class Middlewares(BaseHTTPMiddleware):
    LOG = LogMiddleware(logger=logger)
    SECURITY = SecurityMiddleware()

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Main entry when call this class in fastapi.add_middleware.

        Args:
            - request: client request detail including url, json body, etc.
            - call_next: to call the endpoint/next process
        """
        start_time = time.time()
        await Middlewares.LOG.record_req(request=request)

        auth_header = request.headers.get("Authorization", "")
        try:
            sub_id, sub, session_id = Middlewares.SECURITY.authenticate_user(
                auth_header=auth_header, path=request.url.path
            )
        except HTTPException as exc:
            return JSONResponse(
                content=BaseFailResponse(detail=exc.detail).model_dump(),
                status_code=exc.status_code,
                headers=exc.headers,
            )

        if any([sub_id, sub, session_id]):
            request.state.session_id = session_id
            request.state.username = sub
            request.state.user_id = sub_id

        response = await call_next(request)

        total_time = time.time() - start_time
        Middlewares.LOG.record_resp(response=response, time=total_time)

        return response
