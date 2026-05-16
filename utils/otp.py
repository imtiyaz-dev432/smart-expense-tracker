import os
from flask_mail import Message
from extension import mail


def send_otp_mail(to_email, otp, purpose="verification"):
    subject = "Your Smart Expense Tracker OTP"

    if purpose == "reset":
        subject = "Reset Password OTP - Smart Expense Tracker"

    msg = Message(
        subject=subject,
        sender=os.getenv("MAIL_USERNAME"),
        recipients=[to_email]
    )

    msg.body = f"""
Hello,

Your OTP is: {otp}

This OTP is valid for 3 minutes.

Do not share this OTP with anyone.

Smart Expense Tracker
"""

    mail.send(msg)