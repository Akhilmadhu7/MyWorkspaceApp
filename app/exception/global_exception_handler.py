from fastapi import Request, status
from fastapi.responses import JSONResponse
from exception.exceptions import NotFoundException, CustomException, TimeOutException, ObjectAlreadyExistsException
from typing import Any
from fastapi import FastAPI


UNKNOWN_ERROR:str = "An unknown error occurred. Please try again later."

def global_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundException)
    async def not_found_exception(request:Request,exc: NotFoundException):
        detail:Any = exc.detail if exc.detail else UNKNOWN_ERROR
        status_code:status = exc.status_code if exc.status_code else  status.HTTP_404_NOT_FOUND
        return JSONResponse(
            status_code=status_code,
            content={"detail": detail},
        )


    @app.exception_handler(CustomException)
    async def custom_exception(request:Request, exc: CustomException):
        detail:Any = exc.detail if exc.detail else UNKNOWN_ERROR
        status_code:status = exc.status_code if exc.status_code else status.HTTP_400_BAD_REQUEST
        return JSONResponse(
            status_code=status_code,
            content={"detail":detail}
        )
    
    @app.exception_handler(TimeOutException)
    async def timeout_exception(request:Request, exc:TimeOutException):
        detail:Any = exc.detail if exc.detail else UNKNOWN_ERROR
        status_code:status = exc.status_code if exc.status_code else  status.HTTP_400_BAD_REQUEST
        return JSONResponse(
            status_code=status_code,
            content={"detail":detail}
        )


