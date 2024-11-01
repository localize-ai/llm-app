from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_places():
    return {"places": ["New York", "London", "San Francisco", "Los Angeles"]}