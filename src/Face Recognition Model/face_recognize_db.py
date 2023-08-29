from pymongo import MongoClient
from datetime import datetime
# Replace with your MongoDB connection string
mongo_uri = "mongodb+srv://dinhquan1003:Qu10102003@face-recognize.q8z57n5.mongodb.net/"
userFace = MongoClient(mongo_uri)

# Access a specific database
db = userFace["info_face"]
collection = db["date_face"]
