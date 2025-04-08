import os

# Application settings
SECRET_KEY = '836e866adc266389e1806bc928e20fc0bc5cfe26ac13a451'
DEBUG = True

# Database settings
SQLALCHEMY_DATABASE_URI = 'sqlite:///financial_dashboard.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# AI API settings
AI_API_BASE_URL = "https://mango-bush-0a9e12903.5.azurestaticapps.net/api/v1"
AI_API_KEY = "b69daf09-9d0c-449d-8d87-b30d1fda739a"

# Alpha Vantage API settings
ALPHA_VANTAGE_API_KEY = "KAFJ4O9W4HJGZOAU"