
"""
import os
import resend

resend.api_key = os.environ["RESEND_API_KEY"]


inp = str(input("Enter your email: "))
inp2 = str(input("Enter your Birthday !: "))
#if the user birthday is today, send email happy birthday here is your 10% discount, If not then send email today is not your birthday :(



params: resend.Emails.SendParams = {
    "from": "Acme <onboarding@resend.dev>",
    "to": ["delivered@resend.dev"],
    "subject": "hello world",
    "html": "<strong>it works!</strong>",
}

email = resend.Emails.send(params)
print(email)

# export RESEND_API_KEY="re_hvyieuHn_5AuTPDB4RFSV3HspKZZH9WvT"   
#./venv/bin/python /Users/d-23-6840/Desktop/movie/workings/send_email.py

"""
import os
import resend
from datetime import datetime

resend.api_key = os.environ["RESEND_API_KEY"]

user_email = input("Enter your email: ")
birthday_input = input("Enter your Birthday (MM-DD): ")

today = datetime.now().strftime("%m-%d")

if birthday_input == today:
    subject = "Happy Birthday! 🎂"
    content = "<strong>Happy Birthday! Here is your 10% discount: BDAY10</strong>"

else:
    subject = "Not your birthday yet!"
    content = "<strong>Today is not your birthday :( But stay tuned for future offers!</strong>"

params: resend.Emails.SendParams = {
    "from": "Acme <onboarding@resend.dev>",
    "to": [user_email], 
    "subject": subject,
    "html": content,
}

try:
    email = resend.Emails.send(params)
    print(f"Email sent successfully! ID: {email['id']}")
except Exception as e:
    print(f"Failed to send email: {e}")


# export RESEND_API_KEY="re_hvyieuHn_5AuTPDB4RFSV3HspKZZH9WvT"   
#./venv/bin/python /Users/d-23-6840/Desktop/movie/workings/send_email.py