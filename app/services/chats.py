from fastapi import WebSocket, WebSocketDisconnect, WebSocketException,status, HTTPException, Request
from websocket_manager import WebSocketConnectionManager
from api.v1.schemas import OneToOneChatSchema, ChatAcknowldgementSchema
from uuid import UUID
from pydantic import ValidationError
from typing import Optional, List
from logger.logger import logger
from enums import MessageStatusEnum, MessageTypeEnum
from database.models import Message
from repository import MessageRepository
import json


class ChatService:

    def __init__(self,message_repo:MessageRepository, websocket_manager:WebSocketConnectionManager):
        self.message_repo = message_repo
        self.websocket_manager = websocket_manager

    
    async def send(self, websocket:WebSocket, user_id:UUID):
        
        await self.websocket_manager.connect(websocket, user_id)

        #after connecting, Messages with status sent exists or not. If it does, then send those messages to users.
        is_non_delivered_message_exists:bool = await self.message_repo.non_delivered_message_exists(websocket.scope['tenant_id'], user_id)
        logger.info(f"Non delivered messages exits: {is_non_delivered_message_exists}")
        if is_non_delivered_message_exists:
            non_delivered_messages:List[dict] = await self.message_repo.get_messages(
                websocket.scope['tenant_id'],
                [MessageStatusEnum.SENT],
                filters={
                    "receiver_id":user_id
                }
            )
            message_ids:List[int] = await self.websocket_manager.broadcast_non_delivered_messages(user_id, non_delivered_messages)
            logger.info(f"Message ids needs to be updated are: {message_ids}")
            await self.message_repo.bulk_update_status(websocket.scope['tenant_id'], message_ids, MessageStatusEnum.DELIVERED)
            logger.info(f"Successfully updated message status to delivered.")
        
        try:
            while True:
                logger.info(f"Connceting for the websocket: {websocket} and user_id: {user_id}")
                message_type:dict = await websocket.receive()
                logger.info(f"Message type is: {message_type} ")
                if message_type.get("type") == "websocket.disconnect":
                    logger.info(f"User: {user_id} disconnecting from the webscoket: {websocket}.")
                    await self.websocket_manager.close(user_id)
                    break

                data = message_type.get("text", None)
                logger.info(f"type of data before checking. {type(data)}.")
                if data is None:
                    logger.error(f"No data from the request.")
                    await self.websocket_manager.publish_message("no data", user_id)
                    continue

                if isinstance(data, str):
                    try:
                        data = json.loads(data)
                    except json.JSONDecodeError:
                        logger.info(f"Invalid JSON: {data}")
                        await self.websocket_manager.publish_message("Invalid JSON format", user_id)
                        continue

                logger.info(f"After laoding teh daa and it's type is : {type(data)}")
                if not isinstance(data, dict):
                    logger.info(f"Type of data is not valid dict, type: {type(data)}.")
                    await self.websocket_manager.publish_message(f"Invalid type of data : {type(data)}.", user_id)
                    continue
                
                try:
                    validated_data = OneToOneChatSchema(**data)
                    logger.info(f"Validated data {validated_data}")
                except ValidationError as e:
                    logger.info(f"Validation error from pydantic validation. Error: {e}")
                    await self.websocket_manager.publish_message(str(e), user_id)
                    continue
                except Exception as e:
                    logger.error(f"Error occurred while validating data. Error: {e}.")
                    await self.websocket_manager.publish_message(str(e), user_id)
                    continue
                
                logger.info(f"Data from websocket: {data} and host: {websocket.client.host}")
                target_user_id:UUID = validated_data.target_user_id
                #create the paylaod to insert into message table
                message_payload:dict = {
                    "sender_id":user_id,
                    "receiver_id":target_user_id,
                    "message":validated_data.message,
                    "message_status":MessageStatusEnum.SENT,
                    "message_type":validated_data.message_type,
                    "tenant_id":websocket.scope['tenant_id']
                }
                message = await self.message_repo.create(message_payload)
                logger.info(f"Added message to database. {type(message)} and message is: {message}")
                await self.websocket_manager.publish_message(message, target_user_id, user_id)
                
        except (WebSocketDisconnect, WebSocketException) as e:
            logger.error(f"error from websocket: {e} and user_id:{user_id} and websocket: {websocket}")
            await self.websocket_manager.close(user_id)
    
    async def update_message_status(self, request:Request, payload:ChatAcknowldgementSchema) ->bool:
        
        tenant_id = request.headers.get("X-Tenant-Id", None)
        payload:dict = payload.model_dump()
        message_ids:List[int] = [message_id for message_id in payload.get("message_ids")]
        logger.info(f"Message ids need to be updated are: {message_ids}")
        await self.message_repo.bulk_update_status(tenant_id,message_ids, payload.get("message_status"))
        return True

        

    
    
