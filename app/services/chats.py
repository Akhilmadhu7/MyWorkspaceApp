from fastapi import WebSocket, WebSocketDisconnect, WebSocketException,status, HTTPException
from websocket_manager import WebSocketConnectionManager
from api.v1.schemas import OneToOneChatSchema
from uuid import UUID
from pydantic import ValidationError
from typing import Optional
from logger.logger import logger
import json


class ChatService:

    def __init__(self, websocket_manager:WebSocketConnectionManager):
        self.websocket_manager = websocket_manager
    
    async def send(self, websocket:WebSocket, user_id:UUID):

        await self.websocket_manager.connect(websocket, user_id)
        try:
            while True:
                logger.info(f"Connceting for the websocket: {websocket} and user_id: {user_id}")
                message_type:dict = await websocket.receive()
                logger.info(f"Message type is: {message_type} ")
                if message_type.get("type") == "websocket.disconnect":
                    logger.info(f"User: {user_id} disconnecting from the webscoket: {websocket}.")
                    await self.websocket_manager.close(websocket, user_id)
                    break

                data = message_type.get("text", None)
                logger.info(f"type of data before checking. {type(data)}.")
                if not data:
                    logger.error(f"No data from the request.")
                    await self.websocket_manager.send_message("no data", user_id)
                    continue

                if isinstance(data, str):
                    try:
                        data = json.loads(data)
                    except json.JSONDecodeError:
                        logger.info(f"Invalid JSON: {data}")
                        await self.websocket_manager.send_message("Invalid JSON format", user_id)
                        continue

                logger.info(f"After laoding teh daa and it's type is : {type(data)}")
                if not isinstance(data, dict):
                    logger.info(f"Type of data is not valid dict, type: {type(data)}.")
                    await self.websocket_manager.send_message(f"Invalid type of data : {type(data)}.", user_id)
                    continue
                
                try:
                    validated_data = OneToOneChatSchema(**data)
                    logger.info(f"Validated data {validated_data}")
                except ValidationError as e:
                    logger.info(f"Validation error from pydantic validation. Error: {e}")
                    await self.websocket_manager.send_message(str(e), user_id)
                    continue
                except Exception as e:
                    logger.error(f"Error occurred while validating data. Error: {e}.")
                    await self.websocket_manager.send_message(str(e), user_id)
                    continue
                
                logger.info(f"Data from websocket: {data} and host: {websocket.client.host}")
                target_user_id:UUID = validated_data.target_user_id
                message:str = validated_data.message
                await self.websocket_manager.send_message(message, target_user_id)
                
        except (WebSocketDisconnect, WebSocketException) as e:
            logger.error(f"error from websocket: {e} and user_id:{user_id} and websocket: {websocket}")
            await self.websocket_manager.close(websocket, user_id)
    
