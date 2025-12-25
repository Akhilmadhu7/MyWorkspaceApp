from fastapi import Request,APIRouter, status

router = APIRouter(prefix='/health')

@router.get("/")
async def check_health(request:Request):
    from exception.exceptions import NotFoundException
    from fastapi import HTTPException, status
    raise NotFoundException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=["raising not found","heyyy"]
    )
    return {
        "status":status.HTTP_200_OK,
        "message":"Success"
    }