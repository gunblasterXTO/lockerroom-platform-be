from typing import Dict, List, Union

from pydantic import BaseModel

from app.core.constants import ResponseStatusMsg


class BaseSuccessResponse(BaseModel):
    status: str = ResponseStatusMsg.SUCCESS.value


class GetSuccessResponse(BaseSuccessResponse):
    data: List[Dict]
    current_page: int
    total_page: int
    limit: int


class PostSuccessResponse(BaseSuccessResponse):
    data: Union[List[Dict], Dict]


class BaseFailResponse(BaseModel):
    status: str = ResponseStatusMsg.FAIL.value
    detail: str | None
