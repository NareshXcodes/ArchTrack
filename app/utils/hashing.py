from passlib.context import CryptContext

pwd_context = CryptContext(schemes = ['Bcrypt'],deprecated="auto")

def hashed_password(plain_password : str):
    return pwd_context.hash(plain_password)

def verifying_password(plain,hashed):
    return pwd_context.verify(plain,hashed)