import logging

from fastapi import FastAPI
from app.router import places_router

app = FastAPI()

app.include_router(places_router.router, prefix="/v1/places", tags=["places"])

logging.basicConfig(level=logging.INFO)
