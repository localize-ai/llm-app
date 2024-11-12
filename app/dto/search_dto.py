from enum import Enum
from fastapi import Query
from pydantic import BaseModel


class SearchCategory(str, Enum):
    work_friendly = "work_friendly"
    classic_vibes = "classic_vibes"
    hidden_gem = "hidden_gem"
    pet_friendly = "pet_friendly"
    cozy_atmosphere = "cozy_atmosphere"


class SearchParam(BaseModel):
    q: str | None = None
    image_url: str | None = None
    category: SearchCategory | None = None
    limit: int = Query(20, ge=1, le=50)
