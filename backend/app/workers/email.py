"""
Email sending background tasks.

Uses arq for async task processing with Redis as broker.
In development, emails go to MailHog (localhost:8025 web UI).
"""

import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import aiosmtplib

from app.config import get_settings

logger = logging.getLogger(__name__)


async def send_email(
    to_email: str,
    subject: str,
    html_body: str,
    text_body: str | None = None,
) -> None:
    """Send an email via SMTP. Skips silently if SMTP is not configured."""
    settings = get_settings()

    # Skip if SMTP host is not configured or is placeholder
    if not settings.smtp_host or settings.smtp_host in ("localhost", "") and settings.is_production:
        logger.info("SMTP not configured, skipping email to %s: %s", to_email, subject)
        return

    message = MIMEMultipart("alternative")
    message["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    message["To"] = to_email
    message["Subject"] = subject

    if text_body:
        message.attach(MIMEText(text_body, "plain"))
    message.attach(MIMEText(html_body, "html"))

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user or None,
            password=settings.smtp_password or None,
            use_tls=settings.smtp_use_tls,
            timeout=5,
        )
        logger.info("Email sent to %s: %s", to_email, subject)
    except Exception:
        logger.warning("Failed to send email to %s (SMTP may not be configured)", to_email)


async def send_verification_email(to_email: str, token: str) -> None:
    settings = get_settings()
    verify_url = f"{settings.frontend_url}/verify-email?token={token}"
    html = f"""
    <h2>Welcome to FiberHub Egypt</h2>
    <p>Please verify your email address by clicking the link below:</p>
    <p><a href="{verify_url}">Verify Email</a></p>
    <p>This link expires in {settings.verification_token_expire_hours} hours.</p>
    <p>If you did not create an account, please ignore this email.</p>
    """
    await send_email(to_email, "Verify your FiberHub Egypt email", html)


async def send_password_reset_email(to_email: str, token: str) -> None:
    settings = get_settings()
    reset_url = f"{settings.frontend_url}/forgot-password?token={token}"
    html = f"""
    <h2>Password Reset Request</h2>
    <p>Click the link below to reset your password:</p>
    <p><a href="{reset_url}">Reset Password</a></p>
    <p>This link expires in {settings.password_reset_token_expire_hours} hour(s).</p>
    <p>If you did not request this, please ignore this email.</p>
    """
    await send_email(to_email, "Reset your FiberHub Egypt password", html)


async def send_rfq_invitation_email(
    to_email: str, rfq_title: str, buyer_company_name: str,
) -> None:
    settings = get_settings()
    rfqs_url = f"{settings.frontend_url}/dashboard/rfqs"
    html = f"""
    <h2>New RFQ Invitation</h2>
    <p>You have been invited to respond to an RFQ:</p>
    <p><strong>{rfq_title}</strong></p>
    <p>From: {buyer_company_name}</p>
    <p><a href="{rfqs_url}">View RFQ Details</a></p>
    """
    await send_email(to_email, f"RFQ Invitation: {rfq_title}", html)


async def send_verification_status_email(
    to_email: str, status: str, admin_notes: str | None = None,
) -> None:
    settings = get_settings()
    dashboard_url = f"{settings.frontend_url}/dashboard/company/verification"
    notes_section = f"<p><strong>Notes:</strong> {admin_notes}</p>" if admin_notes else ""
    html = f"""
    <h2>Verification Update</h2>
    <p>Your verification request has been <strong>{status}</strong>.</p>
    {notes_section}
    <p><a href="{dashboard_url}">View Details</a></p>
    """
    await send_email(to_email, f"Verification {status.title()} — FiberHub Egypt", html)


async def send_new_message_email(
    to_email: str, sender_name: str, thread_subject: str | None = None,
) -> None:
    settings = get_settings()
    messages_url = f"{settings.frontend_url}/dashboard/messages"
    subject_line = f" — {thread_subject}" if thread_subject else ""
    html = f"""
    <h2>New Message</h2>
    <p>You have a new message from <strong>{sender_name}</strong>{subject_line}.</p>
    <p><a href="{messages_url}">Open Messages</a></p>
    """
    await send_email(to_email, f"New message from {sender_name}", html)
