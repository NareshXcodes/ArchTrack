# from app.db.database import SessionDB
# from app.schemas.schema import DecisionCreate ,DecisionResponse, OptionVoteCount
# from fastapi import APIRouter,status,HTTPException,Depends, Response
# from app.utils.oauth2 import get_current_user
# from app.models.users import User
# from app.models.decisions import Decision
# from typing import List

# router = APIRouter(prefix="/decisions",tags=['Decision'])

# @router.get("/{id}",response_model=DecisionResponse)
# def get_decision_detail(id:int, db:SessionDB, current_user: User = Depends(get_current_user)):
#     pass