import os
from dotenv import load_dotenv
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer


# Load the environment variables
load_dotenv()

# MongoDB client setup
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB_NAME")]
embedding_collection = db[os.getenv("MONGO_PLACE_EMBEDDINGS_COLLECTION")]

# Load the CLIP model and tokenizer
model = SentenceTransformer("clip-ViT-L-14")


def combined_search_places(search_phrase, limit=20):
    """
    Search for places based on a search phrase, combining text and image embeddings.
    """
    # Encode the search phrase into a vector
    emb = model.encode(search_phrase)

    # Search separately for text and image embeddings
    text_results = embedding_collection.aggregate(
        [
            {
                "$vectorSearch": {
                    "index": "default",
                    "path": "embedding",
                    "queryVector": emb.tolist(),
                    "numCandidates": 100,
                    "limit": 50,
                    "filter": {"type": "text"},
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "content": 1,
                    "type": 1,
                    "place_id": 1,
                    "score": {"$meta": "vectorSearchScore"},
                }
            },
        ]
    )

    image_results = embedding_collection.aggregate(
        [
            {
                "$vectorSearch": {
                    "index": "default",
                    "path": "embedding",
                    "queryVector": emb.tolist(),
                    "numCandidates": 100,
                    "limit": 50,
                    "filter": {"type": "image"},
                }
            },
            {
                "$project": {
                    "_id": 1,
                    "content": 1,
                    "type": 1,
                    "place_id": 1,
                    "score": {"$meta": "vectorSearchScore"},
                }
            },
        ]
    )

    # Apply a multiplier to image scores to give them more weight
    text_results = list(text_results)
    image_results = list(image_results)

    for result in image_results:
        result["score"] *= 1.25  # Adjust multiplier as needed

    # Combine results
    combined_results = text_results + image_results

    # Distinct results by place_id
    combined_results = {doc["place_id"]: doc for doc in combined_results}.values()

    # Sort the combined results by score
    combined_results = sorted(combined_results, key=lambda x: x["score"], reverse=True)

    # Limit the number of results
    return combined_results[:limit]
