import os
import smtplib
import sys
import traceback
from email.message import EmailMessage


SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def main() -> int:
    sender = os.getenv("GMAIL_SENDER")
    password = os.getenv("GMAIL_PASSWORD")
    recipient = os.getenv("GMAIL_RECIPIENT")

    missing_vars = [
        name
        for name, value in (
            ("GMAIL_SENDER", sender),
            ("GMAIL_PASSWORD", password),
            ("GMAIL_RECIPIENT", recipient),
        )
        if not value
    ]

    if missing_vars:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )

    print("Connecting to SMTP...")

    message = EmailMessage()
    message["Subject"] = "GitHub Action Test"
    message["From"] = sender
    message["To"] = recipient
    message.set_content("Email test successful")

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
            server.starttls()
            server.login(sender, password)
            print("SMTP login successful")
            server.send_message(message)
            print("Email sent")
    except Exception:
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        sys.exit(1)
