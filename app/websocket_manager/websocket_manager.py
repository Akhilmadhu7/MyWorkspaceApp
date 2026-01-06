from fastapi import WebSocket, WebSocketException, status
from uuid import UUID
from typing  import Optional, List, Dict
from logger.logger import logger
from cache import AsyncRedisManager, get_redis
from datetime import datetime, timezone
import json
import asyncio
import uuid

class WebSocketConnectionManager:
    

    def __init__(self, redis_client:AsyncRedisManager):
        self.redis_client = redis_client
        self.local_active_connections:dict[UUID, WebSocket] = {}
        self.channel = lambda user_id : f"user_id: {user_id}"\

    async def connect(self, websocket:WebSocket, user_id:UUID):
        
        #check whether an open connection is exists for the user and pop it if the user has.
        existing_connection = self.local_active_connections.get(user_id)
        if existing_connection:
            logger.error(f"An existing connection for the user_id: {user_id} exists.")
            self.local_active_connections.pop(user_id)
        
            raise WebSocketException(code=status.HTTP_400_BAD_REQUEST, reason="An existing connection.")
        
        #if not, then accept the connection and add the connection to the memory.
        logger.info(f"Connection doesn't exist and creating a new one for the user: {user_id}")
        await websocket.accept()
        logger.info(f"Successfully accepted connection for the user_id: {user_id}")

        self.local_active_connections[user_id] = websocket
        
        #$ubscribe to the user channe.
        asyncio.create_task(self.subscribe_channel(user_id))
    
    async def close(self, user_id:UUID):

        existing_connection = self.local_active_connections.get(user_id)
        if existing_connection:
            logger.info(f"Connection exists for the user_id: {user_id}. removing connection from the active connections.")
            self.local_active_connections.pop(user_id)
            channel:str = self.channel(user_id)
            logger.info(f"channel name to be deleted: {channel}")
            # self.redis_client.delete(channel)
            async with self.redis_client.pubsub() as pubsub:
                await pubsub.unsubscribe(self.channel(user_id))
            logger.info(f"Successfully deleted the channel: {channel}")
    
    async def subscribe_channel(self, user_id:UUID):
        
        #create the channel name
        channel:str = self.channel(user_id)
        logger.info(f"Channel to be listening: {channel}")
    
        async with self.redis_client.pubsub() as pubsub:
            #subscribed to the channel
            await pubsub.subscribe(channel)
            logger.info(f"Subscribed to the channel: {channel}")

            #listening from the subscribed channel.
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    logger.info(f"Message is: {message}")
                    user_id_channel:str = message.get("channel")
                    logger.info(f"user id channel: {user_id_channel}")
                    receiver_user_id:UUID = UUID(user_id_channel.split("user_id: ")[1])
                    logger.info(f"receiver user id in subscribe: {receiver_user_id}")
                    receiver_websocket:WebSocket = self.local_active_connections.get(receiver_user_id)
                    logger.info(f"websocket for the receiver user id: {receiver_websocket}")
                    if receiver_websocket:
                        #get the data and send the message.
                        content:dict = json.loads(message.get("data"))
                        await self.local_active_connections.get(user_id).send_json(content)
 
    async def publish_message(self, message:dict, reciever_id:UUID, sender_id:UUID):
        
        #get the connection.
        client_connection:WebSocket = self.local_active_connections.get(reciever_id)
        logger.info(f"client connnection is: {client_connection}.")

        #If connection exists, then publish the message.
        if client_connection:
            logger.info(f"sending message to the user: {reciever_id} and message: {message}.")
            
            #create the channel name
            channel:str = self.channel(reciever_id)
            logger.info(f"channel is: {channel}")

            #publish the message to the channel
            await self.redis_client.publish(channel, json.dumps(message))
            logger.info(f"Successfully published the message for the reciver_id: {reciever_id} send by user_id: {sender_id}.")

    
    async def broadcast_non_delivered_messages(self, receiver_id:UUID, messsages:List[dict]) -> List[int]:
        receiver_connection:WebSocket = self.local_active_connections.get(receiver_id)
        message_ids:List[int] = []
        for message in messsages:
            logger.info(f"sending non delivered message to the receiver_id: {receiver_id}")
            await receiver_connection.send_json(message)
            message_ids.append(message.get("message_id"))
        return message_ids
        
    # async def broadcast_message(self, reciever_id:UUID):
    #     reciever_history_messages:dict = self.message_history.get(reciever_id)
    #     reciever_connection:WebSocket = self.local_active_connections.get(reciever_id)
    #     logger.info(f"Broadcast messages receiver connection: {reciever_connection}")
    #     for sender_id, json_content in reciever_history_messages.items():
    #         logger.info(f"sending messages through broadcast: {json_content}")
    #         await reciever_connection.send_json(json.loads(json_content))       

websocket_manager:Optional[WebSocketConnectionManager] = None

async def create_websocket_manager():
    redis_client:AsyncRedisManager = await get_redis()
    global websocket_manager
    websocket_manager = WebSocketConnectionManager(redis_client=redis_client)
    logger.info(f"Successfully created websocket: {websocket_manager}")

def delete_websocket_manager():
    global websocket_manager
    websocket_manager.local_active_connections.clear()
    logger.info(f"Successfully deleted the websocket manager.")


def get_websocket_manager():
    if websocket_manager is None:
        logger.error(f"Websocket manager doesn't exist.")
        raise RuntimeError("Websocket connection has not been initialized.")
    return websocket_manager

    


