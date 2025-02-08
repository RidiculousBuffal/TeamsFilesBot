from enum import Enum
from typing import Union, List

from pydantic import BaseModel


class ResultStatus(Enum):
    SUCCESS_CODE = 0
    FAILURE_CODE = 1
    SUCCESS_MESSAGE = "success"


class Result(BaseModel):
    code: int
    message: str
    data: Union[List[dict], dict, List, None, int, str, float, bool]
