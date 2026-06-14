from app.models.users import User
from app.db.database import SessionDB
from fastapi import Depends , APIRouter , HTTPException, status
from app.utils.oauth2 import get_current_user
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app.utils.jwt import create_access_token
from app.utils.hashing import hashed_password , verifying_password
from app.schemas.user import UserCreate , UserResponse , TokenResponse


router = APIRouter(tags=['Authentication'])

@router.post("/login",response_model=TokenResponse)
def login(db:SessionDB, user_credential : OAuth2PasswordRequestForm = Depends()):
    user = db.query(User).filter(User.email == user_credential.username).first()

    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Crediantial"
        )

    if not verifying_password(user_credential.password,user.password):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Crediantial"
        )

    access_token = create_access_token(data={"sub" : user.email})
    return {"access_token" : access_token , "token_type" : "bearer"}

@router.post("/register",response_model=UserResponse,status_code = status.HTTP_201_CREATED)
def register(db:SessionDB, new_user : UserCreate):
    existing_user = db.query(User).filter(new_user.email == User.email).first()

    if existing_user:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail="Email already taken !!"
        )

    new_user.password = hashed_password(new_user.password)
    user = User(**new_user.model_dump())

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/me",response_model=UserResponse)
def current_logged_in_status(current_user : User = Depends(get_current_user)):
    return current_user