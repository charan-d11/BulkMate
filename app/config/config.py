# import os

# GEMINI_API_KEY=os.environ.get("GEMINI_API_KEY")
# NUTRITIONIX_APP_ID=os.environ.get("NUTRITIONIX_APP_ID")
# NUTRITIONIX_API_KEY=os.environ.get("NUTRITIONIX_API_KEY")

# SQLALCHEMY_DATABASE_URI = "sqlite:///weightgain.db"
# SQLALCHEMY_TRACK_MODIFICATIONS = False

import os
from dotenv import load_dotenv

load_dotenv()  # ← This reads your .env file first!

class Config:
    # AI
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    
    # Nutritionix
    NUTRITIONIX_APP_ID = os.environ.get("NUTRITIONIX_APP_ID")
    NUTRITIONIX_API_KEY = os.environ.get("NUTRITIONIX_API_KEY")

    # Database
    #SQLALCHEMY_DATABASE_URI = "sqlite:///weightgain.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///weightgain.db")

    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-secret-key")
    DEBUG = os.environ.get("DEBUG", "True") == "True"