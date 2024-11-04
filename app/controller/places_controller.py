import logging
import time

from app.chain.search_image_chain import SearchImageChain
from app.dto.search_dto import SearchParam
from app.chain.search_text_chain import SearchTextChain


class PlacesController:
    def __init__(self):
        self.search_text_chain = SearchTextChain()
        self.search_image_chain = SearchImageChain()

    def get_places(self, params: SearchParam):
        """
        Get places based on the search query or image URL.
        """

        # Start timer
        start_time = time.time()

        if params.q:
            # Search for places based on the search query
            result = self.search_text_chain.search(params)
            places = result.get("places")
            keyword = result.get("keyword")

            # End the timer
            execution_time = time.time() - start_time
            logging.info(f"The search took {execution_time:.2f} seconds")

            return {
                "data": places,
                "meta": {
                    "execution_time": execution_time,
                    "total_results": len(places),
                    "keyword": keyword,
                    "is_image_search": result.get("is_image_search"),
                },
            }
        elif params.image_url:
            # Search for places based on the image URL
            result = self.search_image_chain.search(params)
            places = result.get("places")

            # End the timer
            execution_time = time.time() - start_time
            logging.info(f"The search took {execution_time:.2f} seconds")

            return {
                "data": places,
                "meta": {
                    "execution_time": execution_time,
                    "total_results": len(places),
                    "image_url": params.image_url,
                },
            }
        else:
            raise ValueError("Either 'q' or 'image_url' must be provided")
