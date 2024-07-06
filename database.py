from pymongo import MongoClient

# uri = "mongodb+srv://admin:admin@cluster0.fl7vscu.mongodb.net/db01?retryWrites=true&w=majority"
uri ="mongodb+srv://admin:DEiN23JNE4SNASDsan32432@cluster0.fl7vscu.mongodb.net/tp-master?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client['lang']  # Use your actual database name
