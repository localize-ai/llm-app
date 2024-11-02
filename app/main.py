import logging
from fastapi import FastAPI
from app.router import places_router

app = FastAPI()

app.include_router(places_router.router, prefix="/v1/places", tags=["places"])

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", port=8080, host="0.0.0.0", reload=True)
