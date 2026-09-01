from app.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session



try:
    engine = create_engine(str(settings.DATABASE_URL), connect_args={"sslmode": "require"}, echo=False)
    sessionLocal = sessionmaker(bind=engine , autocommit=False, autoflush=False)
except Exception as e:
    print(f"Database connection Error, Error : {e}")

class Base(DeclarativeBase):
    pass

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

SessionDB = Annotated[Session, Depends(get_db)]
