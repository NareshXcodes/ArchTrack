from fastapi import HTTPException

ALLOWED_TRANSITIONS = {
    "proposed":     ["under_review"],
    "under_review": ["accepted", "rejected"],
    "accepted":     ["deprecated", "superseded"],
    "rejected":     ["proposed"],   # can be revised and resubmitted
    "deprecated":   [],
    "superseded":   []
}

def validate_transition(current:str,new:str):
    if new not in ALLOWED_TRANSITIONS[current]:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid transition from {current} to {new}"
        )