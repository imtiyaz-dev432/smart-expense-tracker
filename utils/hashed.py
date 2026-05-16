import random
from werkzeug.security import generate_password_hash, check_password_hash


def generate_otp():
    return str(random.randint(100000, 999999))


def hash_otp(otp):
    return generate_password_hash(otp)


def verify_hashed_otp(hashed_otp, plain_otp):
    return check_password_hash(hashed_otp, plain_otp)