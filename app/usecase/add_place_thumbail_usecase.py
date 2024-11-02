def add_places_thumbnail(embeddings: list, places: list):
    """
    Add thumbnail URLs to the places if available from embeddings.
    """
    # Create a dictionary to map place_id to the corresponding place
    place_dict = {place["_id"]: place for place in places}

    # If the embeddings type is image, input the content on images to the places
    for embedding in embeddings:
        place_id = embedding["place_id"]
        if place_id in place_dict:
            place = place_dict[place_id]
            if "images" not in place:
                place["images"] = []
            if embedding["content"] not in place["images"]:
                place["images"].append(embedding["content"])

    # Remove duplicates from the images list (if necessary)
    for place in places:
        if "images" in place:
            place["images"] = list(set(place["images"]))

    return places
