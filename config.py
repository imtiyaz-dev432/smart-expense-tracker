# The working of this page is loading .env 
import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


class Config:
    JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY')
    REDIS_URL=os.getenv("REDIS_URL")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")    
    SQLALCHEMY_TRACK_MODIFICATIONS=False   
    CELERY_BROKER_URL=os.getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND=os.getenv("CELERY_BACKEND_URL")
    SQLALCHEMY_ENGINE_OPTIONS= {"pool_pre_ping": True, "pool_recycle": 300}
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)      # default
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)        # default


class TestingConfig(Config):
    TESTING=True
    RATELIMIT_ENABLED=False
    SQLALCHEMY_DATABASE_URI=os.getenv("TEST_DATABASE_URL")
    JWT_SECRET_KEY=os.getenv("TEST_JWT_SECRET_KEY")
    REDIS_URL = "redis://localhost:6379/15"
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True
