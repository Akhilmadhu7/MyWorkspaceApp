from fastapi import Request,APIRouter, status

router = APIRouter(prefix='/health')

@router.get("/")
async def check_health(request:Request):
    return {
        "status":status.HTTP_200_OK,
        "message":"Success"
    }