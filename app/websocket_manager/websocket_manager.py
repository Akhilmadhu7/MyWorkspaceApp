from fastapi import WebSocket, WebSocketException, status
from uuid import UUID
from typing  import Optional, List, Dict
from logger.logger import logger
from cache import AsyncRedisManager, get_redis
from datetime import datetime, timezone
from config.config import config
import json
import asyncio
import uuid

class WebSocketConnectionManager:

    ONLINE_KEY = "online_users"
    USER_KEY = lambda uuid: f"user:{uuid}"
    

    def __init__(self, redis_client:AsyncRedisManager):
        self.redis_client = redis_client
        self.local_active_connections:dict[UUID, WebSocket] = {}
        self.channel = lambda user_id : f"user_id:{user_id}"
        self.online_connections:List[UUID] = []
        self.server_channel = config.redis_channel_name
        self.listener_task:Optional[asyncio.Task] = None
        self.server_name = config.server_name

    async def start_listener(self):
        if self.listener_task and not self.listener_task.done():
            logger.error(f"Listener exists for the server: {self.server_name} and channel: {self.server_channel}")
            return
        self.listener_task = asyncio.create_task(self.__server_listener())
        logger.info(f"Listener started for the channel: {self.server_channel}")

    async def connect(self, websocket:WebSocket, user_id:UUID):
        
        #check whether an open connection is exists for the user and pop it if the user has.
        existing_connection = self.local_active_connections.get(user_id)
        if existing_connection:
            logger.error(f"An existing connection for the user_id: {user_id} exists.")
            self.local_active_connections.pop(user_id)
            logger.info(f"Replacint the websocker for the user_id: {user_id}")
            # raise WebSocketException(code=status.HTTP_400_BAD_REQUEST, reason="An existing connection.")
        
        #if not, then accept the connection and add the connection to the memory.
        logger.info(f"Connection doesn't exist and creating a new one for the user: {user_id}")
        await websocket.accept()
        logger.info(f"Successfully accepted connection for the user_id: {user_id}")

        self.local_active_connections[user_id] = websocket
        user_data:dict = {
            "server_name":self.server_name,
            "server_channel_name":self.server_channel,
            "connected_at":datetime.now(timezone.utc).isoformat()
        }
        #set the user data in redis
        await self.redis_client.setex(
            f"user_id:{user_id}",
            7200,
            json.dumps(user_data)
        )
    
    async def close(self, user_id:UUID):

        existing_connection = self.local_active_connections.get(user_id)
        if existing_connection:
            logger.info(f"Connection exists for the user_id: {user_id}. removing connection from the active connections.")
            self.local_active_connections.pop(user_id)
        await self.redis_client.delete(f"user_id:{user_id}")

    async def __server_listener(self):
        try:
            async with self.redis_client.pubsub() as pubsub:
                await pubsub.subscribe(self.server_channel)
                logger.info(f"Successfully subscribed to the server: {self.server_channel}")

                async for message in pubsub.listen():
                    if message['type'] == 'message':
                        logger.info(f"Message: {message}")
                        payload:dict = json.loads(message['data'])
                        logger.info(f"payload decoded: {payload}")
                        receiver_user_id:UUID = UUID(payload.get('receiver_id'))

                        receiver_websocket:WebSocket = self.local_active_connections.get(receiver_user_id, None)
                        if receiver_websocket:
                            logger.info(f"Receiver websocker connection exists: {receiver_websocket}")
                            await receiver_websocket.send_json(payload)
                            logger.info(f"Message delivered to the receiver: {receiver_user_id}")
                        else:
                            logger.error(f"Connection doesn't exist for the receiver_id: {receiver_user_id}")
        except Exception as error:
            logger.error(f"Error from server listener: {error}")
        
    async def publish_message(self, message:dict, reciever_id:UUID):
        
        #get user info from redis.
        receiver_data = await self.redis_client.get(f"user_id:{reciever_id}")

        #if  user info, then  publish the message to the user server channle.
        if receiver_data:
            logger.info(f"receiver: {reciever_id} is online.")

            receiver_info:dict = json.loads(receiver_data)
            #get the user server channel
            receiver_server_channel_name:str = receiver_info.get("server_channel_name")
            
            #publish message.
            await self.redis_client.publish(receiver_server_channel_name, json.dumps(message))
        else:
            logger.info(f"receiver: {reciever_id} is offline.")
        

    async def broadcast_non_delivered_messages(self, receiver_id:UUID, messsages:List[dict]) -> List[int]:
        receiver_connection:WebSocket = self.local_active_connections.get(receiver_id)
        message_ids:List[int] = []
        for message in messsages:
            logger.info(f"sending non delivered message to the receiver_id: {receiver_id}")
            await receiver_connection.send_json(message)
            message_ids.append(message.get("message_id"))
        return message_ids
        

websocket_manager:Optional[WebSocketConnectionManager] = None

async def create_websocket_manager():
    redis_client:AsyncRedisManager = await get_redis()
    global websocket_manager
    websocket_manager = WebSocketConnectionManager(redis_client=redis_client)
    logger.info(f"Successfully created websocket: {websocket_manager}")
    return websocket_manager

def delete_websocket_manager():
    global websocket_manager
    websocket_manager.local_active_connections.clear()
    logger.info(f"Successfully deleted the websocket manager.")


def get_websocket_manager():
    if websocket_manager is None:
        logger.error(f"Websocket manager doesn't exist.")
        raise RuntimeError("Websocket connection has not been initialized.")
    return websocket_manager

    


