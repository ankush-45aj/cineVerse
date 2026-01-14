import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Use %40 to represent the '@' in your password
MONGO_URI = "mongodb+srv://jhaankush47_db_user:ankush123@clustertest.wihifmz.mongodb.net/?appName=ClusterTest"

client = MongoClient(MONGO_URI)
db = client["movie_recommendation_db"]
users_collection = db["users"]