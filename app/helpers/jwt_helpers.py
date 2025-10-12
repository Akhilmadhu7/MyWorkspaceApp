import jwt
from datetime import datetime, timedelta, timezone
from dateutil import parser

def create_access_token(data:dict, jwt_algo:str, jwt_secret_key:str, time_in_minutes:int) -> str:
    jwt_data:dict = data.copy()
    jwt_data['expires_at'] = str(datetime.now(timezone.utc) + timedelta(minutes=time_in_minutes))
    jwt_data['iat'] = str(datetime.now(timezone.utc))
    jwt_token = jwt.encode(jwt_data, jwt_secret_key, jwt_algo)
    return jwt_token

def create_refresh_token(data:dict, jwt_algo:str, jwt_secret_key:str, time_in_minutes:int) -> str:
    jwt_data:dict = data.copy()
    jwt_data['expires_at'] = str(datetime.now(timezone.utc) + timedelta(minutes=time_in_minutes))
    jwt_data['iat'] = str(datetime.now(timezone.utc))
    jwt_data['tokey_type'] = 'refresh'
    jwt_token = jwt.encode(jwt_data, jwt_secret_key, jwt_algo)
    return jwt_token

jwt_data = {"user_id":123, "role":"owner"}

def verify_token(jwt_token:str, jwt_algo:str, jwt_secret_key:str) -> bool:
    
    try:
        data = jwt.decode(jwt_token, jwt_secret_key, [jwt_algo])
        jwt_expires_at = parser.parse(data['expires_at'])
        current_time = datetime.now(timezone.utc)
        if current_time > jwt_expires_at:
            return False
        # if data.get("user_id")
        
    except jwt.InvalidAlgorithmError as e:
        pass
    except jwt.InvalidSignatureError as e:
        pass
    except jwt.ExpiredSignatureError as e:
        pass
    except jwt.InvalidTokenError as e:
        pass
