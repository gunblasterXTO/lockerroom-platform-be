from fastapi import FastAPI, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.settings import Settings
from app.helpers.response import BaseFailResponse, BaseSuccessResponse
from app.middleware import Middlewares
from app.v1 import v1_router


app = FastAPI(title=Settings.PROJECT_NAME, version=Settings.VERSION)
app.add_middleware(Middlewares)
app.include_router(v1_router)


@app.get("/")
async def health_check() -> str:
    return "Server is working"


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    return JSONResponse(
        content=BaseFailResponse(detail="Validation error").model_dump(),
        status_code=status.HTTP_400_BAD_REQUEST,
    )
