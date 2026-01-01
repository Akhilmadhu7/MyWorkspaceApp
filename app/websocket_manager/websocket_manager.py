from fastapi import WebSocket, WebSocketException, status
from uuid import UUID
from typing  import Optional
from logger.logger import logger

class WebSocketConnectionManager:
    

    def __init__(self):
        self.active_connections:dict[UUID, WebSocket] = {}
        self.message_history:dict[UUID, dict] = {}

    async def connect(self, websocket:WebSocket, user_id:UUID):
        
        existing_connection = self.active_connections.get(user_id)
        if existing_connection:
            logger.error(f"An existing connection for the user_id: {user_id} exists.")
            self.active_connections.pop(user_id)
            raise WebSocketException(code=status.HTTP_400_BAD_REQUEST, reason="An existing connection.")
        logger.info(f"Connection doesn't exist and creating a new one for the user: {user_id}")
        await websocket.accept()
        logger.info(f"Successfully accepted connection for the user_id: {user_id}")
        self.active_connections[user_id] = websocket
        logger.info(f"message history for the user_id: {user_id} and messages: {self.message_history.get(user_id)}")
        if user_id in self.message_history and self.message_history[user_id]:
            logger.info(f"user_id: {user_id} in message history.")
            await self.broadcast_message(user_id)


    async def close(self, user_id:UUID):
        existing_connection = self.active_connections.get(user_id)
        if existing_connection:
            logger.info(f"Connection exists for the user_id: {user_id}. removing connection from the active connections.")
            self.active_connections.pop(user_id)
        
    async def send_message(self, message:str, user_id:UUID):
        client_connection:WebSocket = self.active_connections.get(user_id)
        logger.info(f"client connnection is: {client_connection}.")
        if client_connection:
            logger.info(f"sending message to the user: {user_id} and message: {message}.")
            await client_connection.send_json(message)
        elif self.message_history.get(user_id, None):
            logger.info(f"message history exists for the user_id: {user_id} and updating the user message history.")
            self.message_history[user_id].update({user_id:message})
        else:
            logger.info(f"Message history doesn't exist for the user_id: {user_id}. Adding the message to the user")
            self.message_history[user_id] = {user_id:message}
        
        
    async def broadcast_message(self, reciever_id:UUID):
        reciever_history_messages:dict = self.message_history.get(reciever_id)
        reciever_connection:WebSocket = self.active_connections.get(reciever_id)
        logger.info(f"Broadcast messages receiver connection: {reciever_connection}")
        for sender_id, message in reciever_history_messages.items():
            logger.info(f"sending messages through broadcast: {message}")
            await reciever_connection.send_json(message)

websocket_manager:Optional[WebSocketConnectionManager] = None

def create_websocket_manager():
    global websocket_manager
    websocket_manager = WebSocketConnectionManager()
    logger.info(f"Successfully created websocket: {websocket_manager}")

def delete_websocket_manager():
    global websocket_manager
    websocket_manager.active_connections.clear()
    logger.info(f"Successfully deleted the websocket manager.")


def get_websocket_manager():
    if websocket_manager is None:
        logger.error(f"Websocket manager doesn't exist.")
        raise RuntimeError("Websocket connection has not been initialized.")
    return websocket_manager

    


