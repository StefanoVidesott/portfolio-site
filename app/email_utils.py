import os
import smtplib
import sentry_sdk

from email.message import EmailMessage
from app.schemas import ContactRequest

SMTP_SERVER = os.getenv("SMTP_SERVER", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL", "")


def send_email_task(contact: ContactRequest) -> None:
    msg = EmailMessage()
    msg.set_content(
        f"Nuovo messaggio dal tuo Portfolio!\n\n"
        f"Nome: {contact.name}\n"
        f"Email: {contact.email}\n\n"
        f"Messaggio:\n{contact.message}"
    )
    msg["Subject"] = f"Nuovo Contatto da: {contact.name}"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        print(f"Errore invio email: {e}")
