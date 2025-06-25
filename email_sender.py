# email_sender.py
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

def send_email(winner_name):
    email_address =  os.getenv("EMAIL_USER")
    email_password = os.getenv("EMAIL_PASS")  # gunakan environment variable dalam implementasi asli

    msg = EmailMessage()
    msg['Subject'] = 'Selamat!'
    msg['From'] = email_address
    msg['To'] = f"{winner_name}@gmail.com"
    msg.set_content(f"Selamat {winner_name}, kamu menang tebak angkanya!")

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email_address, email_password)
            smtp.send_message(msg)
        print("[EMAIL] Email terkirim.")
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")