from pydantic import BaseModel
from typing import Any,Union, TypeVar,Generic
from .pagination import Pagination

T = TypeVar("T")

class BaseResponse(BaseModel, Generic[T]):
    data:T|None
    message:str
    status:Union[str, int]
    error: str | list[str] | None = None
    pagination: Pagination | None = None
    @classmethod
    def model_json_schema(cls, *args, **kwargs):
        schema = super().model_json_schema(*args, **kwargs)
        # if this model doesn't actually use pagination, drop it
        if not getattr(cls, "__include_pagination__", True):
            schema["properties"].pop("pagination", None)
            # also remove from required if present
            if "required" in schema:
                schema["required"] = [
                    f for f in schema["required"] if f != "pagination"
                ]
        return schema



    