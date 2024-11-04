# Load the environment variables
import os
from dotenv import load_dotenv
from pymongo import MongoClient

from app.helper.object_id_converter import convert_object_id_to_str

load_dotenv()

# MongoDB client setup
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB_NAME")]
places_collection = db[os.getenv("MONGO_PLACES_COLLECTION")]


def get_places_by_ids(embeddings: list):
    """
    Get places by their IDs from the database.
    """
    ids = [place["place_id"] for place in embeddings]

    # Find the places based on the provided IDs
    places = places_collection.aggregate(
        [
            {
                "$match": {
                    "_id": {"$in": ids},
                },
            },
            {
                "$addFields": {
                    "index": {"$indexOfArray": [ids, "$_id"]},
                },
            },
            {
                "$sort": {
                    "index": 1,
                },
            },
        ]
    )

    # Add score to the places
    places = list(convert_object_id_to_str(places))
    for i, place in enumerate(places):
        place["score"] = embeddings[i]["score"]

    # Convert the ObjectIds to strings
    return places
