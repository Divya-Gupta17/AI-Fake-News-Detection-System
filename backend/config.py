# import os

# class Config:
#     SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_super_secret_key_here' # Change this!
#     MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/fakenewsdb'

#     # API Keys - GET THESE FROM YOUR ACCOUNTS
#     NEWS_API_KEY = os.environ.get('NEWS_API_KEY') or 'YOUR_NEWS_API_KEY' # Get from newsapi.org
#     GOOGLE_FACT_CHECK_API_KEY = os.environ.get('GOOGLE_FACT_CHECK_API_KEY') or 'YOUR_GOOGLE_FACT_CHECK_API_KEY' # Get from Google Cloud Console (Custom Search API, Knowledge Graph API, etc.)
#     # Note: Google Fact Check API is not a direct product, often involves Custom Search API or Knowledge Graph API
#     # You might need to enable a specific Google Cloud API for fact-checking capabilities.
#     # For a direct "fact-check" tool, consider the ClaimReview schema data available via Custom Search API.

#     # Model Configuration (should match train_bert.py)
#     BERT_MODEL_NAME = 'bert-base-uncased'
#     MAX_LEN = 128
#     MODEL_PATH = '../model_save/' # Relative path from backend/app.py

#     # Frontend URL (for CORS)
#     FRONTEND_URL = os.environ.get('FRONTEND_URL') or 'http://localhost:3000'


# import os

# class Config:
#     # Flask
#     SECRET_KEY = os.environ.get('SECRET_KEY') or 'change_this_super_secret_key'

#     # Mongo
#     MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/fakenewsdb'

#     # External APIs
#     NEWS_API_KEY = os.environ.get('NEWS_API_KEY') or 'e06a6c523c2e4d1d8e6989bdc26e09e1'     # newsapi.org
    
#     # ✅ FIXED: Do NOT use os.environ.get() if direct value
#     GOOGLE_FACT_CHECK_API_KEY = "AIzaSyAQpbuh50uJfkV2vOZcy81YIjUdhbFRGzE"
#     GOOGLE_CSE_ID = "1723393488c6c46d3"

#     # Models
#     BERT_MODEL_NAME = 'bert-base-uncased'
#     MAX_LEN = 128
#     MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'model_save')





import os

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change_this_super_secret_key'

    # MongoDB
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017'
    MONGO_DB_NAME = "fakenewsdb"

    # External APIs
    NEWS_API_KEY = os.environ.get('NEWS_API_KEY') or 'e06a6c523c2e4d1d8e6989bdc26e09e1'
    
    GOOGLE_FACT_CHECK_API_KEY = "AIzaSyAQpbuh50uJfkV2vOZcy81YIjUdhbFRGzE"
    GOOGLE_CSE_ID = "1723393488c6c46d3"

    # ---------------- Models ----------------
    # THIS is correct for your structure!
    MODEL_PATH = os.path.join(os.path.dirname(__file__), "model_save")

    MAX_LEN = 128

    # HF model for user dashboard
    HF_MODEL_NAME = "hamzab/roberta-fake-news-classification"

    DEBUG = True
