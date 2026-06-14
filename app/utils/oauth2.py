from app.utils.jwt import verify_access_token
from fastapi.security import OAuth2PasswordBearer
from app.db.database import SessionDB
from fastapi import Depends , HTTPException , status
from app.models.users import User

oauth2_schema = OAuth2PasswordBearer(tokenUrl='/login')

def get_current_user(db:SessionDB , token: str = Depends(oauth2_schema)):
    credential_exception = HTTPException(
        status_code =status.HTTP_401_UNAUTHORIZED,
        detail = "Could not validate credentials",
        headers = {"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_access_token(token, credential_exception)
    user = db.query(User).filter(User.email == token_data).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user