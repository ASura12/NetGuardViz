from pymongo import MongoClient
from app.core.config import MONGODB_URI, MONGODB_DB_NAME

client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB_NAME]

users_collection = db["users"]
logs_collection = db["logs"]
alerts_collection = db["alerts"]

# logs = logs_collection.find().skip(skip).limit(limit)
# logs = list(logs)