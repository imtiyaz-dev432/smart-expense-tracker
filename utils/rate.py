import os

from flask import request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0?protocol=2")


def get_ip_identity() -> str:
    return f"ip:{get_remote_address()}"


def get_contact_identity() -> str:
    if request.is_json:
        data = request.get_json(silent=True)
        if isinstance(data, dict):
            email = data.get("email")
            if isinstance(email, str) and email.strip():
                return f"email:{email.strip().casefold()}"

            mobile = data.get("mobile_no")
            if mobile is not None and str(mobile).strip():
                return f"mobile:{str(mobile).strip()}"

    return get_ip_identity()


def get_login_identity() -> str:
    if request.is_json:
        data = request.get_json(silent=True)
        if isinstance(data, dict):
            username = data.get("username")
            if isinstance(username, str) and username.strip():
                return f"username:{username.strip().casefold()}:{get_remote_address()}"

    return get_ip_identity()


limiter = Limiter(
    key_func=get_ip_identity,
    default_limits=["200 per day", "50 per hour"],#different gunicorn
    #workers runn each worker take 49,49 and there is a

# #10 worker then requet reach in 1 hour is 490 due to this reason i use default limits

# # and in redis counters are deletd after some tume but in db we need to delete manually

# #and in race condition redis count

# # always helpful bcz here db shayad crash ho jaaye


    storage_uri=REDIS_URL,
    strategy="fixed-window",   #In rate limiting (and specifically in flask-limiter),
    # Fixed Window divides time into discrete, static blocks
    # # (for example, 12:00–12:01, 12:01–12:02). Every request arriving inside that
    # #specific clock block increments a single counter, and when the clock ticks over
    # to the next block, the counter resets to zero.
)
