from fastapi import HTTPException,status
import uuid
from datetime import datetime
from datetime import timedelta
import jwt
import token
from config import settingJWT

def create_access_token(data: dict,expires_delta:timedelta=timedelta(hours=2)):
    return jwt.encode(
        payload={
           "user":{
            **data
           },
           "exp": datetime.now() + expires_delta,
           "jti":str(uuid.uuid4()),
        },
        key=settingJWT.jwt_secret,
        algorithm=settingJWT.jwt_algorithm
    )
    
def decode_access_token(token: str):
    try:
        return jwt.decode(
            jwt=token,
            key=settingJWT.jwt_secret,
            algorithms=[settingJWT.jwt_algorithm]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
   