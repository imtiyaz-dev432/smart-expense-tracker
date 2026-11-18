import os

from flask import request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

REDIS_URL=os.getenv("REDIS_URL","redis://localhost:6379/0?protocol=2")

def get_identity():
    if request.is_json:
        data=request.get_json(silent=True) or {}
        identifier=data.get("email") or data.get("mobile_no")
        if identifier:
            return str(identifier)
    return get_remote_address()

limiter=Limiter(
    key_func=get_identity,
    default_limits=["200 per day", "50 per hour"], #if there is a
    #different gunicorn workers runn each worker take 49,49 and there is a
    # #10 worker then requet reach in 1 hour is 490 due to this reason i use default limits
    # # and in redis counters are deletd after some tume but in db we need to delete manually
    # #and in race condition redis count
    # # always helpful bcz here db shayad crash ho jaaye
    storage_uri=REDIS_URL

)
