from fastapi import status
from typing import Any

class CustomException(Exception):

    def __init__(self, detail:Any, status_code:status = status.HTTP_400_BAD_REQUEST) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail, status_code)
    
class NotFoundException(Exception):

    def __init__(self, detail:Any, status_code:status = status.HTTP_404_NOT_FOUND) -> None:
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail, status_code)





