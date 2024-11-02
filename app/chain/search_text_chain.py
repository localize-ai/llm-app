import logging

from app.dto.search_dto import SearchParam
from app.usecase.add_place_thumbail_usecase import add_places_thumbnail
from app.usecase.get_places_by_ids_usecase import get_places_by_ids
from app.usecase.get_embedding_places_usecase import combined_search_places
from app.usecase.keyword_generator_usecase import generate_keyword


class SearchTextChain:

    # Search for places based on a search query and optional category
    def search(self, dto: SearchParam):
        """
        Search for places based on a search query and optional category.
        """
        # Generate a keyword string based on the search query and category
        keyword = generate_keyword(dto.q, dto.category)
        logging.info(f"Generated keyword: {keyword}")

        # Search for places based on the generated keyword
        embeddings = combined_search_places(keyword)
        logging.info(f"Found {len(embeddings)} embeddings")

        # Get detailed information for each place
        places = get_places_by_ids(embeddings)
        logging.info(f"Retrieved detailed information for {len(places)} places")

        # Add thumbnail URLs to the places if available from embeddings
        add_places_thumbnail(embeddings, places)

        return {
            "places": places,
            "keyword": keyword,
        }
