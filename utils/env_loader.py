import os

from dotenv import load_dotenv

load_dotenv()

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
SECRET_KEY = os.environ.get("SECRET_KEY")
POSTGRES_USER = os.environ.get("POSTGRES_USER")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD")
POSTGRES_DOMAIN = os.environ.get("POSTGRES_DOMAIN")
POSTGRES_DB = os.environ.get("POSTGRES_DB")
EMAIL = os.environ.get("EMAIL")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
FRONTEND_URL = os.environ.get("FRONTEND_URL")
SQS_URL = os.environ.get("SQS_URL")
AWS_REGION_NAME = os.environ.get("AWS_REGION_NAME")
APP_URL = os.environ.get("APP_URL")
