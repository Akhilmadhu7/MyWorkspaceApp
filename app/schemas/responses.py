from pydantic import BaseModel
from typing import Any,Union

class BaseResponse(BaseModel):
    data:Any
    message:str
    status:Union[str, int]

    