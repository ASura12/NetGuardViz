import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import SMTP_SERVER, SMTP_PORT, EMAIL_ADDRESS, EMAIL_PASSWORD, TO_EMAIL


def _require_config(name: str, value: str | None) -> str:
    if not value:
        raise RuntimeError(f"Missing required email config: {name}")
    return value

def send_alert_notification(alert: dict):

    smtp_server = _require_config("SMTP_SERVER", SMTP_SERVER)
    email_address = _require_config("EMAIL_ADDRESS", EMAIL_ADDRESS)
    email_password = _require_config("EMAIL_PASSWORD", EMAIL_PASSWORD)
    to_email = _require_config("TO_EMAIL", TO_EMAIL)

    subject = "🚨 Security Alert Detected"

    body = f"""
Security Alert Triggered

File: {alert['filename']}
Keywords: {alert['detected_keywords']}
Time: {alert['timestamp']}
"""

    message = MIMEMultipart()
    message["From"] = email_address
    message["To"] = to_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(smtp_server, SMTP_PORT) as server:
        server.starttls()
        server.login(email_address, email_password)
        server.send_message(message)