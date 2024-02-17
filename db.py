import json
# Import database configuration from database.py
from database import db

verbs_collection = db['verbs']

def load_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def insert_verbs(data):
    result = verbs_collection.insert_many(data)
    print(f"{len(result.inserted_ids)} documents inserted.")

if __name__ == "__main__":
    file_path = 'upload.json'
    data = load_data(file_path)
    insert_verbs(data)
