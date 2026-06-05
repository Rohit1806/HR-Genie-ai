import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class EmailSender:
    """Email sending service."""

    def __init__(self):
        # TODO: Configure SMTP settings from env
        self.smtp_host = ""
        self.smtp_port = 587
        self.from_email = "noreply@hrgenie.ai"

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachments: Optional[List[str]] = None,
    ) -> bool:
        """Send an email."""
        # TODO: Implement SMTP sending
        logger.info(f"Email sent to {to}: {subject}")
        return True

    async def send_password_reset(self, to: str, reset_url: str) -> bool:
        subject = "HRGenie - Password Reset Request"
        body = f"Click the link to reset your password: {reset_url}"
        return await self.send_email(to, subject, body)

    async def send_leave_notification(self, to: str, employee_name: str, leave_type: str, dates: str) -> bool:
        subject = f"Leave Request from {employee_name}"
        body = f"{employee_name} has requested {leave_type} leave for {dates}. Please review in HRGenie."
        return await self.send_email(to, subject, body)


email_sender = EmailSender()
