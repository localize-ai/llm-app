import logging
from app.dto.search_dto import SearchParam
from app.usecase.add_place_thumbail_usecase import add_places_thumbnail
from app.usecase.get_places_by_ids_usecase import get_places_by_ids
from app.usecase.get_places_by_image_usecase import image_vector_search


class SearchImageChain:
    def search(self, dto: SearchParam):
        """
        Search for places based on an image URL.
        """
        # Search for places based on the image URL
        embeddings = image_vector_search(dto.image_url)
        logging.info(f"Found {len(embeddings)} embeddings")

        # Get detailed information for each place
        places = get_places_by_ids(embeddings)
        logging.info(f"Retrieved detailed information for {len(places)} places")

        # Add thumbnail URLs to the places if available from embeddings
        places = add_places_thumbnail(embeddings, places)

        return {
            "places": places,
        }
