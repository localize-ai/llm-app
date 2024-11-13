import os
import requests

from dotenv import load_dotenv
from pymongo import MongoClient
from PIL import Image
from io import BytesIO

from sentence_transformers import SentenceTransformer
from transformers import CLIPTokenizer

clip_model = SentenceTransformer("clip-ViT-L-14")
clip_tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-large-patch14")

# Load the environment variables
load_dotenv()

# MongoDB client setup
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB_NAME")]
embedding_collection = db[os.getenv("MONGO_PLACE_EMBEDDINGS_COLLECTION")]
place_reviews_collection = db[os.getenv("MONGO_PLACES_REVIEWS_COLLECTION")]


def generate_text_embedding(text):
    tokens = clip_tokenizer.encode(
        text, truncation=True, max_length=77, add_special_tokens=True
    )
    tokens = tokens[
        :77
    ]  # Ensure the token length matches the model's expected input length

    # Encode the truncated text
    return clip_model.encode(tokens, convert_to_tensor=True).tolist()


def generate_image_embedding(image_url):
    # Fetch the image from the URL
    response = requests.get(image_url)
    response.raise_for_status()  # Ensure the request was successful
    image = Image.open(BytesIO(response.content))

    # Generate the embedding
    return clip_model.encode(
        image,
        convert_to_tensor=True,
        device="cuda",
    ).tolist()


# place_id
# rating = number
# review = string
# images = array
# user
def insert_vector(data: dict):
    """
    Insert the vector into the MongoDB collection.
    """
    try:
        review_text = f"review: {data['review']}; rating: {data['rating']}"
        text_embedding = generate_text_embedding(review_text)
        embedding_collection.insert_one(
            {
                "place_id": data["place_id"],
                "type": "review_text",
                "content": review_text,
                "embedding": text_embedding,
            }
        )
    except Exception as e:
        print(f"Error generating text embedding: {e}")

    try:
        for image_url in data["images"]:
            image_embedding = generate_image_embedding(image_url)
            embedding_collection.insert_one(
                {
                    "place_id": data["place_id"],
                    "type": "image",
                    "content": image_url,
                    "embedding": image_embedding,
                }
            )
    except Exception as e:
        print(f"Error generating image embedding: {e}")
