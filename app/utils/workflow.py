from fastapi import HTTPException

ALLOWED_TRANSITIONS = {
    "proposed" : ["under_review"],
    "under_review" : ["accepted","proposed"],
    "accepted" : ["deprecated","superseded"],
    "deprecated" : [],
    "superseded" : []
}

def validate_transition(current:str,new:str):
    if new not in ALLOWED_TRANSITIONS[current]:
        raise HTTPException(status_code=400, detail="Invalid transition")