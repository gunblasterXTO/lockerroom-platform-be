from fastapi import FastAPI, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.settings import Settings
from app.db.sql import Database
from app.helpers.exceptions import (
    BadClientReqeust,
    ConflictClientRequest,
    InternalServerError,
    UnauthorizedClientRequest,
)
from app.helpers.response import BaseFailResponse
from app.middleware import Middlewares
from app.v1 import v1_router


app = FastAPI(title=Settings.PROJECT_NAME, version=Settings.VERSION)
app.add_middleware(Middlewares)
app.include_router(v1_router)


@app.get("/health/server", include_in_schema=False)
async def health_check() -> Response:
    return Response(content="Server is working")


@app.get("/health/db", include_in_schema=False)
async def health_check_db() -> Response:
    try:
        sess = Database().session()
        sess.execute(text("SELECT 1"))
    except SQLAlchemyError as err:
        return Response(
            content=f"DB encounter issue: {err}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    else:
        return Response(content="DB is working")
    finally:
        sess.close()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    return JSONResponse(
        content=BaseFailResponse(detail="Validation error").model_dump(),
        status_code=status.HTTP_400_BAD_REQUEST,
    )


@app.exception_handler(BadClientReqeust)
async def bad_request_handler(
    request: Request, exc: BadClientReqeust
) -> JSONResponse:
    return JSONResponse(
        content=BaseFailResponse(detail=exc.message).model_dump(),
        status_code=status.HTTP_400_BAD_REQUEST,
    )


@app.exception_handler(UnauthorizedClientRequest)
async def unauthorized_request_handler(
    request: Request, exc: UnauthorizedClientRequest
) -> JSONResponse:
    return JSONResponse(
        content=BaseFailResponse(detail=exc.message).model_dump(),
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(ConflictClientRequest)
async def conflict_request_handler(
    request: Request, exc: ConflictClientRequest
) -> JSONResponse:
    return JSONResponse(
        content=BaseFailResponse(detail=exc.message).model_dump(),
        status_code=status.HTTP_409_CONFLICT,
    )


@app.exception_handler(InternalServerError)
async def internal_server_error_handler(
    request: Request, exc: InternalServerError
) -> JSONResponse:
    return JSONResponse(
        content=BaseFailResponse(detail=exc.message).model_dump(),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
