import json
import requests
import time
import os

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from PIL import Image
from io import BytesIO
from transformers import CLIPTokenizer
from pymongo import MongoClient

# Load the environment variables
load_dotenv()

# Load the CLIP model and tokenizer
model = SentenceTransformer("clip-ViT-L-14")
tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-large-patch14")

# MongoDB client setup
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB_NAME")]
places_collection = db[os.getenv("MONGO_PLACES_COLLECTION")]
place_reviews_collection = db[os.getenv("MONGO_PLACES_REVIEWS_COLLECTION")]
embedding_collection = db[os.getenv("MONGO_PLACE_EMBEDDINGS_COLLECTION")]


def generate_text_embedding(text):
    tokens = tokenizer.encode(
        text, truncation=True, max_length=77, add_special_tokens=True
    )
    truncated_text = tokenizer.decode(tokens, skip_special_tokens=True)

    # Encode the truncated text
    return model.encode(truncated_text, convert_to_tensor=True).tolist()


def generate_image_embedding(image_url):
    # Fetch the image from the URL
    response = requests.get(image_url)
    response.raise_for_status()  # Ensure the request was successful
    image = Image.open(BytesIO(response.content))

    # Generate the embedding
    return model.encode(
        image,
        convert_to_tensor=True,
        device="cuda",
    ).tolist()


# Function to process data and insert into MongoDB
def process_and_insert_data(input_data):
    start_time = time.time()  # Start the timer
    index = 0

    for place in input_data:
        index += 1
        each_place_start_time = time.time()

        # Add image embeddings for `thumbnail` (if not null), `images`, and `user_reviews`
        image_urls = [img["image"] for img in place["images"]]

        if place["thumbnail"] is not None:
            image_urls.insert(0, place["thumbnail"])

        if place["user_reviews"] is not None:
            for review in place["user_reviews"]:
                image_urls.extend(review.get("Images", []))

        # Create the main dictionary structure
        place_doc = {
            "_id": place["cid"],
            "title": place["title"],
            "categories": place["categories"],
            "address": place["address"],
            "review_count": place["review_count"],
            "review_rating": place["review_rating"],
            "description": place["description"],
            "open_hours": place["open_hours"],
            "popular_times": place["popular_times"],
            "web_site": place["web_site"],
            "phone": place["phone"],
            "plus_code": place["plus_code"],
            "reviews_per_rating": place["reviews_per_rating"],
            "latitude": place["latitude"],
            "longtitude": place["longtitude"],
            "reviews_link": place["reviews_link"],
            "price_range": place["price_range"],
            "menu": place["menu"],
            "reservations": place["reservations"],
            "order_online": place["order_online"],
            "about": place["about"],
            "images": image_urls,
        }

        # Insert the place document into the places collection and get the inserted ID, if error duplicate key, then continue to next place
        try:
            place_id = places_collection.insert_one(place_doc).inserted_id
        except Exception as e:
            print(f"Error inserting place i: {index}: {e}")
            continue

        # Insert user reviews into the place_reviews collection
        if place["user_reviews"] is not None:
            place_reviews_collection.insert_many(
                [
                    {
                        "place_id": place_id,
                        "rating": review["Rating"],
                        "review": review["Description"],
                        "images": review.get("Images", []),
                        "user": None,
                    }
                    for review in place["user_reviews"]
                ]
            )

        try:
            # Generate text embedding
            text = f"title: {place['title']}; description: {place['description']}; address: {place['address']}"
            text_embedding = generate_text_embedding(text)

            # Insert text embedding as a separate document in the embeddings collection
            embedding_collection.insert_one(
                {
                    "place_id": place_id,
                    "type": "text",
                    "content": text,
                    "embedding": text_embedding,
                }
            )
        except Exception as e:
            print(f"Error generating text embedding for place {place['title']}: {e}")

        # Generate embeddings for each image URL
        for url in image_urls:
            try:
                image_embedding = generate_image_embedding(url)
                embedding_collection.insert_one(
                    {
                        "place_id": place_id,
                        "type": "image",
                        "content": url,
                        "embedding": image_embedding,
                    }
                )
            except Exception as e:
                print(f"Error generating embedding for image {url}: {e}")
                continue

        # Insert text embedding for each user review with rating > 3
        if place["user_reviews"] is not None:
            for review in place["user_reviews"]:
                review_text = f"review: {review['Description']}; rating: {review['Rating']}"
                try:
                    review_embedding = generate_text_embedding(review_text)
                    embedding_collection.insert_one(
                        {
                            "place_id": place_id,
                            "type": "review_text",
                            "content": review_text,
                            "embedding": review_embedding,
                        }
                    )
                except Exception as e:
                    print(f"Error generating text embedding for review: {review_text}: {e}")
                    continue

        print(
            f"Processed {index} places in each place in {time.time() - each_place_start_time:.2f} seconds"
        )

    print(f"Processed {index} places in {time.time() - start_time:.2f} seconds")


# Input data getting data from public_space.json file
input_data = json.load(open("localize_ai_app/data/public_space.json"))

# Process the input data
process_and_insert_data(input_data)
