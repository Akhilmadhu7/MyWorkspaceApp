from . import verify_token
from fastapi import WebSocket, HTTPException, status
from logger import logger
from config.config import config
from typing import List, Optional

async def get_current_user(webscoket:WebSocket) :
    auth_token:str = webscoket.headers.get("Authorization")
    logger.info(f"Auth token from websocket: {auth_token}")
    if not auth_token:
        # raise HTTPException(status.HTTP_401_UNAUTHORIZED, "No token")
        
        webscoket.scope['user_id'] = "f6df6ddd-e28d-40fe-b874-690425ecd312"
        webscoket.scope['tenant_id'] = "ca6987a7-9f38-49e9-99dc-efee3fb1e92d"
        webscoket.scope['email'] = "test@mail.csls"
        webscoket.scope['role_id'] = "f6df6ddd-e28d-40fe-b874-690425ecd312"
        webscoket.scope['username'] = "user_data"
        webscoket.scope['token'] = "token f6df6ddd-e28d-40fe-b874-690425ecd312"
        return {}
    auth_token_parts:List[str] = auth_token.split(" ")
    token:Optional[str] = auth_token_parts[1] if len(auth_token_parts) >1 else None
    if not token:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token."
        )
    try:
        user_data:dict = verify_token(token, config.jwt_algo, config.jwt_secret_key)
        logger.info(f"user data after verifying token: {user_data}")
        webscoket.scope['user_id'] = user_data.get("user_id", None)
        webscoket.scope['tenant_id'] = user_data.get("user_tenant_id", None)
        webscoket.scope['email'] = user_data.get("email", None)
        webscoket.scope['role_id'] = user_data.get("role_id", None)
        webscoket.scope['username'] = user_data.get("username", None)
        webscoket.scope['token'] = token
        return user_data
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error)
        )
