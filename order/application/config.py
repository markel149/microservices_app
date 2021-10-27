from os import environ
from dotenv import load_dotenv
import requests
import json

# Only needed for developing, on production Docker .env file is used
load_dotenv()


class Config:
    """Set Flask configuration vars from .env file."""
    # Database
    SQLALCHEMY_DATABASE_URI = environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = environ.get("SQLALCHEMY_TRACK_MODIFICATIONS")
    # print(SQLALCHEMY_DATABASE_URI)
    
    #auth_public_key = json.loads(requests.get("http://auth:8000/client/get_public_key").content)['public_key']
