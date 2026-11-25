import os

import requests  #can be used for communicating with the 3rd party api's
from celery import shared_task


@shared_task() #Bhai, @shared_task — ek decorator jo function
# ko Celery task banata hai — bina app instance se bound kiye
def send_async_email(email, subject, body):
    try:
        api_key = os.getenv("BREVO_API_KEY")
        from_email = os.getenv("FROM_EMAIL")
        from_name = os.getenv("FROM_NAME", "smart-expense-tracker")

        if not api_key:
            raise ValueError("Brevo Api key is missing")
        if not from_email:
            print("Email sending failed: FROM_EMAIL is missing")
            return

        url = "https://api.brevo.com/v3/smtp/email"

        payload = {
            "sender": {
                "name": from_name,
                "email": from_email    #This is strictly dictated by the Brevo API design.
                # Email APIs are built to handle bulk sends, meaning they expect an array
                # #(a list) of multiple recipients
            },
            "to": [
                {
                    "email": email
                }
            ],
            "subject": subject,
            "textContent": body
        }

        headers = {
            "accept": "application/json",
            "api-key": api_key,
            "content-type": "application/json"
        }


        response = requests.post(url, json=payload, headers=headers, timeout=10) #it send the
        #payload to  brevo
        print(f"🔍 Brevo Status: {response.status_code}")
        print(f"🔍 Brevo Body: {response.text}")


        if response.status_code not in [200, 201, 202]:
            print(f"❌ Email FAILED. Status: {response.status_code}, Body: {response.text}")
            return   # ← ye add kar



        print("Email sent successfully to:", email)

    except Exception as e:
        print("Email sending failed:", str(e))


def send_otp_mail(email, otp, purpose="verification"):
    if purpose == "verification":
        subject = "Verify your email - Smart Expense Tracker"
        body = f"Your verification OTP is: {otp}"
    elif purpose in ["forgot_password","reset"]:
        subject = "Reset your password - Smart Expense Tracker"
        body = f"Your password reset OTP is: {otp}"
    else:
        subject = "Your OTP - Smart Expense Tracker"
        body = f"Your OTP is: {otp}"

    send_async_email.delay(email, subject, body)
