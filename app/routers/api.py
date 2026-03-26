import os
import httpx

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.schemas import ContactRequest
from app.email_utils import send_email_task

router = APIRouter()

TURNSTILE_SECRET_KEY = os.getenv("TURNSTILE_SECRET_KEY", "")


@router.post("/api/contact")
async def handle_contact(contact: ContactRequest, background_tasks: BackgroundTasks):
    if TURNSTILE_SECRET_KEY:
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
                raise HTTPException(status_code=400, detail="Controllo anti-spam fallito.")

    background_tasks.add_task(send_email_task, contact)
    return {"status": "success", "message": "Email is being sent"}
