


# auth.py
from flask import session, redirect, url_for, jsonify, request
from functools import wraps
from db import users, user_preferences
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

def register_user(username, password):
    if not username or not password:
        return False, "Username and password are required."

    if users.find_one({"username": username}):
        return False, "Username already exists."

    password_hash = generate_password_hash(password)

    user_doc = {
        "username": username,
        "password": password_hash,
        "is_admin": False,
        "created_at": datetime.utcnow()
    }

    user_id = users.insert_one(user_doc).inserted_id

    # Default prefs
    user_preferences.insert_one({
        "user_id": user_id,
        "topics": ["Technology"],
        "sources": [],
        "type": "all",
        "updated_at": datetime.utcnow()
    })

    # Auto-login
    session["logged_in"] = True
    session["user_id"] = str(user_id)
    session["username"] = username
    session["is_admin"] = False

    return True, str(user_id)

def login_user(username, password):
    user = users.find_one({"username": username})

    if not user:
        return False, "Invalid username or password."

    if not check_password_hash(user["password"], password):
        return False, "Invalid username or password."

    # Return user document (so caller can set session fields)
    return True, user

def logout_user():
    session.clear()

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("user_id"):
            return f(*args, **kwargs)

        # For API/AJAX calls return JSON 401 instead of redirect to login HTML
        if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"message": "Unauthorized"}), 401

        return redirect(url_for("login_page"))
    return wrapper

def get_user_preferences(user_id):
    try:
        uid = ObjectId(user_id)
    except:
        return None

    prefs = user_preferences.find_one({"user_id": uid})
    user = users.find_one({"_id": uid})

    if not prefs or not user:
        return None

    return {
        "topics": prefs.get("topics", []),
        "sources": prefs.get("sources", []),
        "type": prefs.get("type", "all"),
        "username": user.get("username")
    }

def update_user_preferences(user_id, new_prefs):
    try:
        uid = ObjectId(user_id)
    except:
        return False

    allowed = {"topics", "sources", "type"}
    update_data = {k: v for k, v in new_prefs.items() if k in allowed}

    if not update_data:
        return False

    update_data["updated_at"] = datetime.utcnow()
    user_preferences.update_one({"user_id": uid}, {"$set": update_data}, upsert=True)
    return True
