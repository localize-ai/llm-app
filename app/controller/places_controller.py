import logging
import time

from app.dto.search_dto import SearchParam
from app.chain.search_text_chain import SearchTextChain


class PlacesController:
    def __init__(self):
        self.search_text_chain = SearchTextChain()

    def get_places(self, params: SearchParam):
        """
        Get places based on the search query or image URL.
        """

        # Start timer
        start_time = time.time()

        if params.q:
            # Search for places based on the search query
            result = self.search_text_chain.search(params)

            # End the timer
            execution_time = time.time() - start_time
            logging.info(f"The search took {execution_time:.2f} seconds")

            return {
                "data": result,
                "meta": {
                    "execution_time": execution_time,
                    "total_results": len(result),
                },
            }
        elif params.image_url:
            pass
        else:
            raise ValueError("Either 'q' or 'image_url' must be provided")
