# The working of this page is loading .env 
import os
from dotenv import load_dotenv
from flask_sqlalchemy  import SQLAlchemy
from datetime import timedelta
load_dotenv()


class Config:
    JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY')
    REDIS_URL=os.getenv("REDIS_URL")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")    
    SQLALCHEMY_TRACK_MODIFICATIONS=False   
    CELERY_BROKER_URL=os.getenv("CELERY_BROKER_URL")
    CELERY_BACKEND_URL=os.getenv("CELERY_BACKEND_URL")
    SQLALCHEMY_ENGINE_OPTIONS= {"pool_pre_ping": True, "pool_recycle": 300}
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)      # default
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)        # default

    