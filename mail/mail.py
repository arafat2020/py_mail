import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from email.message import EmailMessage
from aiosmtplib import send
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel, EmailStr, Field

# Load environment variables
load_dotenv()

# Set up logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# FastAPI router
router = APIRouter(prefix="/email", tags=["Email"])


# Pydantic model for request validation
class SendEmailRequest(BaseModel):
    to: EmailStr = Field(..., description="Recipient's email address")
    subject: str = Field(..., description="Subject of the email")
    firstName: str = Field(..., description="Sender's first name")
    lastName: str = Field(..., description="Sender's last name")
    email: EmailStr = Field(..., description="Sender's email address")
    number: str = Field(..., description="Sender's phone number")
    message: str = Field(..., description="Message from the sender")


# Helper function to send email
async def send_email(to: str, subject: str, body: dict):
    message = EmailMessage()
    message["From"] = os.getenv("MAIL_FROM")
    message["To"] = to
    message["Subject"] = subject
    message.set_content("You have a new booking inquiry. Please view in an HTML-compatible client.")

    html_body = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>{subject}</title>
      <style>
        body {{
          font-family: Arial, sans-serif;
          background-color: #f4f4f4;
          padding: 20px;
          margin: 0;
        }}
        .email-container {{
          background-color: #ffffff;
          max-width: 600px;
          margin: 0 auto;
          padding: 30px;
          border-radius: 8px;
          box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        h2 {{
          color: #006B66;
          margin-top: 0;
        }}
        ul {{
          padding-left: 20px;
        }}
        li {{
          margin-bottom: 10px;
        }}
        .footer {{
          margin-top: 30px;
          font-size: 12px;
          color: #999999;
          text-align: center;
        }}
      </style>
    </head>
    <body>
      <div class="email-container">
        <h2>{subject}</h2>
        <p>You have received a new inquiry with the following details:</p>
        <ul>
          <li><strong>First Name:</strong> {body['firstName']}</li>
          <li><strong>Last Name:</strong> {body['lastName']}</li>
          <li><strong>Email:</strong> {body['email']}</li>
          <li><strong>Phone Number:</strong> {body['number']}</li>
          <li><strong>Message:</strong> {body['message']}</li>
        </ul>
        <div class="footer">
          &copy; {datetime.now().year} Your Company. All rights reserved.
        </div>
      </div>
    </body>
    </html>
    """

    message.add_alternative(html_body, subtype="html")

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


# FastAPI route
@router.post("/send_email")
async def send_email_route(data: SendEmailRequest, background_tasks: BackgroundTasks):
    email_data = {
        "firstName": data.firstName,
        "lastName": data.lastName,
        "email": data.email,
        "number": data.number,
        "message": data.message,
    }
    background_tasks.add_task(send_email, data.to, data.subject, email_data)
    return {"message": f"Email sent to {data.to}"}
