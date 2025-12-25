from pydantic import BaseModel
class Pagination(BaseModel):

    total_records:int
    page_size:int
    page_num:int
    has_next:bool
    has_prev:bool
    is_first:bool
    is_last:bool