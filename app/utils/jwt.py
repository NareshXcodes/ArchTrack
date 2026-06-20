from jose import jwt , JWTError
from datetime import datetime , timedelta, timezone
from app.config import settings


def create_access_token(data:dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode , str(settings.SECRET_KEY), algorithm=str(settings.ALGORITHM))
    return encoded_jwt

def verify_access_token(token: str,credentials_exception):
    try:
        payload = jwt.decode(token, str(settings.SECRET_KEY), algorithms=[str(settings.ALGORITHM)])
        subject: str = payload.get("user_id")
        if subject is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return subject
