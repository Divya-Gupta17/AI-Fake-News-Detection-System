# from pymongo import MongoClient
# from config import Config

# client = MongoClient(Config.MONGO_URI)
# db = client.get_database()

# # Collections
# users = db["users"]
# news = db["news"]          # processed & classified news
# raw_news = db["raw_news"]  # (optional) raw articles




# from pymongo import MongoClient

# client = MongoClient("mongodb://localhost:27017")
# db = client["fakenewsdb"]

# # Collections
# users = db["users"]
# user_preferences = db["user_preferences"]   # ✅ MUST EXIST
# news = db["news"]

# reports = db["reports"]



# db.py
from pymongo import MongoClient
from config import Config

client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
db = client[Config.MONGO_DB_NAME]

# Collections
users = db["users"]
user_preferences = db["user_preferences"]
news = db["news"]
reports = db["reports"]
saved_articles = db["saved_articles"] 
# Ensure indexes
# def ensure_indexes():
#     try:
#         users.create_index("username", unique=True)
#         user_preferences.create_index("user_id", unique=True)
#         news.create_index("url", unique=True)
#         news.create_index([("topic", 1), ("published_at", -1)])
#         reports.create_index("url")
#     except Exception as e:
#         print("Warning: failed to create indexes:", e)

# ensure_indexes()


def ensure_indexes():
    try:
        users.create_index("username", unique=True)
        user_preferences.create_index("user_id", unique=True)
        news.create_index("url", unique=True)
        news.create_index([("topic", 1), ("published_at", -1)])
        reports.create_index("url")
        saved_articles.create_index(
            [("user_id", 1), ("url", 1)], unique=True
        )  # 👈 one article per user per URL
    except Exception as e:
        print("Warning: failed to create indexes:", e)

