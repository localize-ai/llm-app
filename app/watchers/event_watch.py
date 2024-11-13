from bson.json_util import dumps
from event_logic import (
    insert_vector,
    place_reviews_collection,
)


def watch_events():
    """
    Watch the change stream for the place reviews collection.
    """
    while True:
        try:
            change_stream = place_reviews_collection.watch()
            for change in change_stream:
                # Insert the vector into the collection
                if change["operationType"] == "insert":
                    insert_vector(change["fullDocument"])
                print(dumps(change))
        except Exception as e:
            print(f"Error occurred: {e}")


if __name__ == "__main__":
    watch_events()
