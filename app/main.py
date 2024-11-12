import logging

from fastapi import FastAPI
from app.router import places_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(places_router.router, prefix="/v1/places", tags=["places"])

logging.basicConfig(level=logging.INFO)
