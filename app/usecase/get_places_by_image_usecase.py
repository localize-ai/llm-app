from io import BytesIO
import os
import requests

from PIL import Image
from dotenv import load_dotenv
from pymongo import MongoClient

from app.model.clip_model import clip_model

# Load the environment variables
load_dotenv()

# MongoDB client setup
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB_NAME")]
embedding_collection = db[os.getenv("MONGO_PLACE_EMBEDDINGS_COLLECTION")]


def image_vector_search(image_url, limit=20):
    """
    Search for places based on an image URL.
    """
    response = requests.get(image_url)
    response.raise_for_status()  # Ensure the request was successful
    image = Image.open(BytesIO(response.content))
    emb = clip_model.encode(
        image,
        convert_to_tensor=True,
        device="cpu",
    )
    cursor = embedding_collection.aggregate(
        [
            {
                "$vectorSearch": {
                    "index": "default",
                    "path": "embedding",
                    "queryVector": emb.tolist(),
                    "numCandidates": 100,
                    "limit": limit,
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "content": 1,
                    "type": 1,
                    "place_id": 1,
                    "score": {
                        "$meta": "vectorSearchScore",
                    },
                }
            },
        ]
    )

    return list(cursor)
