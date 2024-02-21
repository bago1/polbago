import json
import logging
from database import db

verbs_collection = db['verbs2']
cached_data = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_data_from_mongo():
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

def upload_json_data(file_path):
    """
    Load data from a JSON file.

    :param file_path: Path to the JSON file.
    :return: Data loaded from the JSON file.
    """
    global cached_data
    if cached_data is None:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                cached_data = json.load(file)
                logger.info(f"Data loaded successfully from {file_path}.")
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            cached_data = []
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from file: {file_path}")
            cached_data = []
    return cached_data

if __name__ == "__main__":
    file_path = 'upload2.json'
    data = upload_json_data(file_path)
    insert_verbs(data)







