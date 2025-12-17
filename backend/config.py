


import os

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change_this_super_secret_key'

    # MongoDB
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017'
    MONGO_DB_NAME = "fakenewsdb"

    # External APIs
    NEWS_API_KEY = os.environ.get('NEWS_API_KEY') or 'fill the api '
    
    GOOGLE_FACT_CHECK_API_KEY = "fill the api"
    GOOGLE_CSE_ID = "case id"

    # ---------------- Models ----------------
    # THIS is correct for your structure!
    MODEL_PATH = os.path.join(os.path.dirname(__file__), "model_save")

    MAX_LEN = 128

    # HF model for user dashboard
    HF_MODEL_NAME = "hamzab/roberta-fake-news-classification"

    DEBUG = True
