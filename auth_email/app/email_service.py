import logging

import httpx

from .config import settings

logger = logging.getLogger("auth.email")


def send_verification_email(to: str, code: str) -> None:
    """Send the OTP via Resend. Runs in a background task, so it never blocks the request."""
    if settings.dev_print_otp:
        logger.warning("[DEV] verification code for %s: %s", to, code)
        return

    if not settings.resend_api_key:
        logger.error("RESEND_API_KEY is not set; cannot send email to %s", to)
        return

    minutes = settings.otp_ttl_minutes
    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:480px;margin:auto">
      <h2>Verify your email</h2>
      <p>Use this code to finish signing up for {settings.app_name}:</p>
      <p style="font-size:32px;letter-spacing:8px;font-weight:bold">{code}</p>
      <p>It expires in {minutes} minutes. If you didn't request it, ignore this email.</p>
    </div>
    """
    text = (
        f"Your {settings.app_name} verification code is {code}. "
        f"It expires in {minutes} minutes."
    )

    try:
        resp = httpx.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {settings.resend_api_key}"},
            json={
                "from": settings.email_from,
                "to": [to],
                "subject": f"Your {settings.app_name} verification code",
                "html": html,
                "text": text,
            },
            timeout=10,
        )
        resp.raise_for_status()
    except httpx.HTTPError:
        logger.exception("Failed to send verification email to %s", to)
