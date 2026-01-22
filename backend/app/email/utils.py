import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Union, Any, Dict
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

# Configure Jinja2
TEMPLATE_DIR = Path(__file__).parent / "templates"
env = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=select_autoescape(['html', 'xml'])
)

def render_email_template(template_name: str, context: Dict[str, Any]) -> str:
    """Render a Jinja2 email template"""
    template = env.get_template(template_name)
    return template.render(**context)

def send_email(
    email_to: Union[str, List[str]],
    subject: str,
    html_content: str,
) -> None:
    """Send an email using SMTP"""
    smtp_host = os.getenv("SMTP_HOST", "localhost")
    smtp_port = int(os.getenv("SMTP_PORT", "1025"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")
    emails_from_email = os.getenv("EMAILS_FROM_EMAIL", "calendint@minet.net")
    emails_from_name = os.getenv("EMAILS_FROM_NAME", "Calend'INT by MiNET")

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
