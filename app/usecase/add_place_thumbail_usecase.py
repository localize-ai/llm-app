def add_places_thumbnail(embeddings: list, places: list):
    """
    Add thumbnail URLs to the places if available from embeddings.
    """
    # Create a dictionary to map place_id to the corresponding place
    place_dict = {place["_id"]: place for place in places}

    # Insert new images at the beginning of the images list
    for embedding in embeddings:
        place_id = embedding["place_id"]
        if place_id in place_dict:
            place = place_dict[place_id]
            if "images" not in place:
                place["images"] = []
            if embedding["content"] not in place["images"]:
                place["images"].insert(0, embedding["content"])

    # Remove duplicates from the images list while preserving order
    for place in places:
        if "images" in place:
            seen = set()
            place["images"] = [x for x in place["images"] if not (x in seen or seen.add(x))]

    return places
