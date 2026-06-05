"""
Notification service for HRGenie AI.
Handles pushing real-time alerts to users via WebSockets and logging them.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)


async def notify_user(
    user_id: str,
    title: str,
    body: str,
    notification_type: str = "info",
) -> None:
    """
    Send a real-time notification to a specific user via WebSockets.
    """
    # Import manager inside the function to avoid circular imports
    try:
        from app.api.v1.ws import manager
        
        notification_id = str(uuid.uuid4())
        message = {
            "id": notification_id,
            "title": title,
            "body": body,
            "type": notification_type,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "read": False,
        }
        
        # Log locally
        logger.info(f"Sending notification to user {user_id}: {title} - {body}")
        
        # Push over websocket
        await manager.send_personal_message(message, user_id)
    except Exception as e:
        logger.error(f"Failed to send websocket notification: {e}")


async def broadcast_notification(
    title: str,
    body: str,
    notification_type: str = "info",
) -> None:
    """
    Broadcast a real-time notification to all connected users.
    """
    try:
        from app.api.v1.ws import manager
        
        notification_id = str(uuid.uuid4())
        message = {
            "id": notification_id,
            "title": title,
            "body": body,
            "type": notification_type,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "read": False,
        }
        
        logger.info(f"Broadcasting notification: {title} - {body}")
        await manager.broadcast(message)
    except Exception as e:
        logger.error(f"Failed to broadcast websocket notification: {e}")
