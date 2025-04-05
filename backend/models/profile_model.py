# models/profile_model.py

import datetime
from pymongo import MongoClient
from bson import ObjectId
from config import config

client = MongoClient(config.MONGO_URI)
db = client.get_default_database()

class ProfileModel:
    @staticmethod
    def create_profile(user_id, name, age, gender, location, lat, lon, description, image_path, audio_path):
        profile = {
            "user_id": ObjectId(user_id),
            "name": name,
            "age": age,
            "gender": gender,
            "location": location,
            "lat": lat,
            "lon": lon,
            "description": description,
            "image_path": image_path,
            "audio_path": audio_path,
            # New date/time stamp
            "created_at": datetime.datetime.utcnow()
        }
        result = db.profiles.insert_one(profile)
        return str(result.inserted_id)

    @staticmethod
    def get_profiles():
        return list(db.profiles.find())
    
    @staticmethod
    def search_profiles(query):
        return list(db.profiles.find({"name": {"$regex": query, "$options": "i"}}))

    @staticmethod
    def get_profile_by_id(profile_id):
        return db.profiles.find_one({"_id": ObjectId(profile_id)})
