from pymongo import MongoClient

uri = "mongodb+srv://admin:admin@cluster0.fl7vscu.mongodb.net/db01?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client['lang']  # Use your actual database name
