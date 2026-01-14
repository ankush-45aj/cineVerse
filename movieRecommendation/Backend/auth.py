import bcrypt
from db import users_collection

class AuthService:
    @staticmethod
    def register_user(username, password):
        if users_collection.find_one({"username": username}):
            return {"error": "User already exists"}

        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        )

        users_collection.insert_one({
            "username": username,
            "password": hashed_password
        })
        return {"message": "User registered successfully"}

    @staticmethod
    def login_user(username, password):
        user = users_collection.find_one({"username": username})
        if not user:
            return {"error": "User not found"}

        # Verification logic for bcrypt
        if bcrypt.checkpw(password.encode("utf-8"), user["password"]):
            return {"message": "Login successful"}
        
        return {"error": "Invalid password"}