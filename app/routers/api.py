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
        raise HTTPException(status_code=503, detail="CAPTCHA service unavailable.")

    shared_client: httpx.AsyncClient = request.app.state.http_client
    try:
        ts_response = await shared_client.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={
                "secret": TURNSTILE_SECRET_KEY,
                "response": contact.turnstile_token,
            },
            timeout=5.0,
        )
        result = ts_response.json()
    except httpx.TimeoutException:
        raise HTTPException(status_code=503, detail="CAPTCHA service unavailable.")
    except Exception:
        raise HTTPException(status_code=503, detail="CAPTCHA service unavailable.")

    if not result.get("success"):
        raise HTTPException(status_code=400, detail="Anti-spam check failed.")

    background_tasks.add_task(send_email_task, contact)
    return {"status": "success", "message": "Email is being sent"}
