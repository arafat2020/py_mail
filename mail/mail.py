import os
from dotenv import load_dotenv
from email.message import EmailMessage
from aiosmtplib import send
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel, EmailStr, Field
import logging

logger = logging.getLogger(__name__)



load_dotenv()

async def send_email(to: str, subject: str, body: str):
    message = EmailMessage()
    message["From"] = os.getenv("MAIL_FROM")
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    try:
        await send(
            message,
            hostname=os.getenv("SMTP_HOST"),
            port=int(os.getenv("SMTP_PORT")),
            use_tls=True,
            username=os.getenv("SMTP_USERNAME"),
            password=os.getenv("SMTP_PASSWORD"),
        )
        logger.info(f"Email sent to {to}")
    except Exception as e:
        logger.error(f"Failed to send email to {to}: {e}")
        

class SendEmailRequest(BaseModel):
    to: EmailStr = Field(..., description="Recipient's email address")
    subject: str = Field(..., description="Subject of the email")
    message: str = Field(..., description="Body of the email (plain text or HTML)")

router = APIRouter(prefix="/email", tags=["Email"])

@router.post("/send_email")
async def send_email_route(data: SendEmailRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email, data.to, data.subject, data.message)
    return {"message": f"Email sent to {data.to}"}