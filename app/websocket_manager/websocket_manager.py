from fastapi import WebSocket, WebSocketException, status
from uuid import UUID
from typing  import Optional
from logger.logger import logger

class WebSocketConnectionManager:
    

    def __init__(self):
        self.active_connections:dict[UUID, WebSocket] = {}

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

    async def close(self, websocket:WebSocket, user_id:UUID):
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
        
    async def broadcast_message(self, message:str):
        for client_connection in self.active_connections.values():
            client_connection.send_json(message)

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

    


