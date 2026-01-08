import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Union

def send_email(
    email_to: Union[str, List[str]],
    subject: str,
    html_content: str,
) -> None:
    smtp_host = os.getenv("SMTP_HOST", "localhost")
    smtp_port = int(os.getenv("SMTP_PORT", "1025"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    emails_from_email = os.getenv("EMAILS_FROM_EMAIL", "admin@calendint.fr")
    emails_from_name = os.getenv("EMAILS_FROM_NAME", "Calend'INT")

    if isinstance(email_to, str):
        email_to = [email_to]

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = f"{emails_from_name} <{emails_from_email}>"
    message["To"] = ", ".join(email_to)

    part = MIMEText(html_content, "html")
    message.attach(part)

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            if smtp_user and smtp_password:
                server.login(smtp_user, smtp_password)
            server.sendmail(emails_from_email, email_to, message.as_string())
    except Exception as e:
        print(f"Failed to send email: {e}")
