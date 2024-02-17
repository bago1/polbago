import json
# Import database configuration from database.py
from database import db

verbs_collection = db['verbs']

verbs_collection = db['verbs']
cached_data = None  # Global variable to store loaded data

def load_data(file_path):
    global cached_data  # Access the global variable
    if cached_data is None:  # Load data only if it's not cached
        with open(file_path, 'r', encoding='utf-8') as file:
            cached_data = json.load(file)
    return cached_data


def insert_verbs(data):
    result = verbs_collection.insert_many(data)
    print(f"{len(result.inserted_ids)} documents inserted.")

if __name__ == "__main__":
    file_path = 'upload.json'
    data = load_data(file_path)
    insert_verbs(data)
