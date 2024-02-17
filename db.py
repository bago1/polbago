import json
import logging
from database import db

verbs_collection = db['verbs']
cached_data = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_data():
    global cached_data
    if cached_data is None:
        logger.info("Fetching data from MongoDB...")
        cached_data = list(verbs_collection.find({}))
        logger.info("Data fetched successfully.")
    else:
        logger.info("Using cached data.")
    return cached_data

def insert_verbs(data):
    result = verbs_collection.insert_many(data)
    logger.info(f"{len(result.inserted_ids)} documents inserted.")

if __name__ == "__main__":
    file_path = 'upload.json'
    data = load_data(file_path)
    insert_verbs(data)
