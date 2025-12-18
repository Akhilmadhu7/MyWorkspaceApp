from fastapi import Request, status
from fastapi.responses import JSONResponse
from exception.exceptions import NotFoundException, CustomException
from typing import Any
from fastapi import FastAPI

def global_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundException)
    async def not_found_exception(request:Request,exc: NotFoundException):
        detail:Any = exc.detail if exc.detail else "Unknow error, Please try again."
        status_code:status = exc.status_code if exc.status_code else  status.HTTP_404_NOT_FOUND
        return JSONResponse(
            status_code=status_code,
            content={"detail": detail },
        )


    @app.exception_handler(CustomException)
    async def custom_exception(request:Request, exc: CustomException):
        detail:Any = exc.detail if exc.detail else "Unknown error, Please try again later."
        status_code:status = exc.status_code if exc.status_code else status.HTTP_400_BAD_REQUEST
        return JSONResponse(
            status_code=status_code,
            content={"detail":detail}
        )


