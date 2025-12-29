from fastapi import WebSocket, APIRouter, status, HTTPException, Depends, WebSocketException, WebSocketDisconnect
from ..schemas import BaseResponse
from dependancies import get_chat_service
from services import ChatService
from uuid import UUID

router = APIRouter(prefix="/ws")

@router.websocket(
    "/chat/{user_id}"
)
async def send_chat(
    websocket:WebSocket,
    user_id:UUID,
    chat_service:ChatService = Depends(get_chat_service)
) -> BaseResponse:
    response = await chat_service.send(websocket, user_id)
    return {"success":True}