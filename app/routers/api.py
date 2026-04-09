import os
import httpx

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request

from app.schemas import ContactRequest
from app.email_utils import send_email_task
from app.limiter import limiter

router = APIRouter()

TURNSTILE_SECRET_KEY = os.getenv("TURNSTILE_SECRET_KEY", "")


@router.post("/api/contact")
@limiter.limit("5/hour")
async def handle_contact(
    request: Request,
    contact: ContactRequest,
    background_tasks: BackgroundTasks,
):
    if not TURNSTILE_SECRET_KEY:
        # Fail closed: a missing secret key is a misconfiguration, not a reason
        # to skip verification. Returning 503 signals the operator, not the user.
        raise HTTPException(status_code=503, detail="CAPTCHA service unavailable.")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={
                "secret": TURNSTILE_SECRET_KEY,
                "response": contact.turnstile_token,
            },
        )
        result = response.json()
        if not result.get("success"):
            raise HTTPException(status_code=400, detail="Anti-spam check failed.")

    background_tasks.add_task(send_email_task, contact)
    return {"status": "success", "message": "Email is being sent"}
