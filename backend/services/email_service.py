import logging
import smtplib
from email.message import EmailMessage

from backend.core.config import settings

logger = logging.getLogger("scriptloom.email")


class EmailDeliveryError(RuntimeError):
    """Raised when an email cannot be sent."""


def send_email(
    to_email: str,
    subject: str,
    text_body: str,
) -> None:
    if not settings.SMTP_HOST:
        raise EmailDeliveryError(
            "SMTP is not configured (SMTP_HOST is empty). Cannot send email."
        )

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    message["To"] = to_email
    message.set_content(text_body)

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            if settings.SMTP_USERNAME:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(message)
    except Exception as e:
        logger.error(f"SMTP send to {to_email} failed: {e}", exc_info=True)
        raise EmailDeliveryError(f"Failed to send email: {e}") from e


def send_password_reset_email(
    to_email: str,
    reset_url: str,
) -> None:
    subject = "Reset your Scriptloom password"
    text_body = (
        "We received a request to reset the password for your Scriptloom account.\n\n"
        f"To choose a new password, open the link below. The link expires in "
        f"{settings.PASSWORD_RESET_TOKEN_TTL_MINUTES} minutes and can only be used once.\n\n"
        f"{reset_url}\n\n"
        "If you did not request a password reset, you can safely ignore this email; "
        "your password will not be changed.\n\n"
        "— Scriptloom"
    )
    send_email(to_email, subject, text_body)
