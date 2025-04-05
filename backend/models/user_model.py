from pymongo import MongoClient
from bson import ObjectId
from config import config

client = MongoClient(config.MONGO_URI)
# Using the default database from the URI (or change to a specific one, e.g., client.nomad_db)
db = client.get_default_database()

class UserModel:
    @staticmethod
    def create_user(email, password_hash):
        result = db.users.insert_one({
            "email": email,
            "password_hash": password_hash
        })
        return str(result.inserted_id)

    @staticmethod
    def find_by_email(email):
        return db.users.find_one({"email": email})
