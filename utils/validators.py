import re


def is_valid_email(email):
    email=email.strip() if email else "" #strip removes if i pass in m@gmail.com\n then "\n" automatically deleted
    pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+(\.[a-zA-Z]{2,})+$'
    return re.fullmatch(pattern,email) is not None

def is_valid_mobile(mobile_no):
    mobile_no=mobile_no.strip() if mobile_no else ""
    pattern1=r'^[6-9]\d{9}$'
    return re.fullmatch(pattern1,mobile_no) is not None

def is_valid_password(password):
    password=password.strip() if password else ""
    pattern2=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&₹]).{8,}$'
    return re.fullmatch(pattern2,password) is not None
