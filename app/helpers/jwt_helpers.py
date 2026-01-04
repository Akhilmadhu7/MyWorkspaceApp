import jwt
from datetime import datetime, timedelta, timezone
from dateutil import parser
from logger import logger

def create_access_token(data:dict, jwt_algo:str, jwt_secret_key:str, time_in_minutes:int) -> str:
    jwt_data:dict = data.copy()
    jwt_data['expires_at'] = str(datetime.now(timezone.utc) + timedelta(minutes=time_in_minutes))
    jwt_data['iat'] = int(datetime.now(timezone.utc).timestamp())
    jwt_token = jwt.encode(jwt_data, jwt_secret_key, jwt_algo)
    return jwt_token

def create_refresh_token(data:dict, jwt_algo:str, jwt_secret_key:str, time_in_minutes:int) -> str:
    jwt_data:dict = data.copy()
    jwt_data['expires_at'] = str(datetime.now(timezone.utc) + timedelta(minutes=time_in_minutes))
    jwt_data['iat'] = int(datetime.now(timezone.utc).timestamp())
    jwt_data['token_type'] = 'refresh'
    jwt_token = jwt.encode(jwt_data, jwt_secret_key, jwt_algo)
    return jwt_token

def verify_token(jwt_token:str, jwt_algo:str, jwt_secret_key:str) -> dict:
    
    try:
        data = jwt.decode(jwt_token, jwt_secret_key, [jwt_algo])
        jwt_expires_at = parser.parse(data['expires_at'])
        current_time = datetime.now(timezone.utc)
        logger.info(f"Jwt verification token expires_at: {jwt_expires_at} and the current time: {current_time}")
        if current_time > jwt_expires_at:
            logger.warning(f"Jwt token verificatin failed. Jwt token expried at: {jwt_expires_at}")
            raise Exception("token has expired.")
        logger.info("Successfully decoded jwt token.")
        return data
    except jwt.InvalidAlgorithmError as e:
        raise e
    except jwt.InvalidSignatureError as e:
        raise e
    except jwt.ExpiredSignatureError as e:
        raise e
    except jwt.InvalidTokenError as e:
        raise e
    except Exception as e:
        raise e
