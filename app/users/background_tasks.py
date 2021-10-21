from pydantic import EmailStr
import httpx
from app import settings


async def send_mail(to_email: EmailStr, subject, content):
    headers = {
        "authorization": f"Bearer {settings.SENDGRID_API_KEY}",
        "content-type": "application/json"
    }
    req = {
        "personalizations": [{'to': [{"email": to_email}]}],
        "from": {"email": settings.SENDGRID_FROM_EMAIL},
        "subject": subject,
        "content": [{"type": "text/plain", "value": content}]
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(settings.SENDGRID_EMAIL_SEND_URL,
                                 json=req,
                                 headers=headers)
    if resp.status_code != 202:
        msg = f"Email error, sendgrid respond with HTTP_{resp.status_code}"
        raise ValueError(msg)
