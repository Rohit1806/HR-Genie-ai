import logging
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task
def send_notification(user_id: str, title: str, body: str, category: str, action_url: str = None):
    """Dispatch notification to user via WebSocket and store in DB."""
    logger.info(f"Sending notification to user {user_id}: {title}")
    # TODO: Store in DB + push via WebSocket connection manager
    return {"status": "sent", "user_id": user_id}


@celery_app.task
def send_email_notification(to_email: str, subject: str, body: str):
    """Send email notification."""
    logger.info(f"Sending email to {to_email}: {subject}")
    # TODO: Implement email sending
    return {"status": "sent", "email": to_email}
