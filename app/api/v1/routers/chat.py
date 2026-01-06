from fastapi import WebSocket, APIRouter, status, HTTPException, Depends, WebSocketException, WebSocketDisconnect, Request
from ..schemas import BaseResponse
from dependancies import get_chat_service
from services import ChatService
from uuid import UUID
from helpers import get_current_user
from ..schemas import ChatAcknowldgementSchema
from logger import logger
router = APIRouter(prefix="/ws")

@router.websocket(
    "/chat/{user_id}"
)
async def send_chat(
    websocket:WebSocket,
    user_id:UUID,
    chat_service:ChatService = Depends(get_chat_service),
    user_data:dict = Depends(get_current_user)
) -> BaseResponse:
    logger.info(f"Before chat service method calling.")
    response = await chat_service.send(websocket, user_id)
    return {"success":True}

@router.post(
    "/chat/acknowledge",
    response_model=BaseResponse[bool],
    status_code=status.HTTP_200_OK
)
async def acknowledge_message_delivered(
    request:Request,
    payload:ChatAcknowldgementSchema,
    chat_service:ChatService = Depends(get_chat_service)
):
    data:bool = await chat_service.update_message_status(request, payload)
    return BaseResponse[bool](
        data=data,
        status=status.HTTP_200_OK,
        message="Successfully acknowledged messages."
    )
