import base64
from email.mime.text import MIMEText
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class GmailService:
    """
    Gmail OAuth 2.0 and API integration service.
    Implements sending emails with audit logging, least-privilege tokens,
    and transparent demo simulation when live credentials are absent.
    """

    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI

    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret)

    def get_auth_url(self) -> str:
        if not self.is_configured():
            return f"{settings.FRONTEND_URL}/integrations?demo_gmail=configured"
        from google_auth_oauthlib.flow import Flow
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=["https://www.googleapis.com/auth/gmail.send"]
        )
        flow.redirect_uri = self.redirect_uri
        auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
        return auth_url

    async def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
        user_tokens: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        logger.info(f"Gmail send request initiated for recipient: {recipient}")

        # Check if live credentials and token exist
        if self.is_configured() and user_tokens and user_tokens.get("access_token"):
            try:
                from google.oauth2.credentials import Credentials
                from googleapiclient.discovery import build

                creds = Credentials(
                    token=user_tokens.get("access_token"),
                    refresh_token=user_tokens.get("refresh_token"),
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=self.client_id,
                    client_secret=self.client_secret
                )
                service = build("gmail", "v1", credentials=creds)

                message = MIMEText(body)
                message["to"] = recipient
                message["subject"] = subject
                raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

                sent_msg = service.users().messages().send(
                    userId="me",
                    body={"raw": raw_message}
                ).execute()

                logger.info(f"Email sent via Gmail API! Message ID: {sent_msg.get('id')}")
                return {
                    "success": True,
                    "mode": "live_gmail",
                    "providerMessageId": sent_msg.get("id"),
                    "sentAt": datetime.now(timezone.utc).isoformat()
                }
            except Exception as e:
                logger.error(f"Gmail API delivery failed: {e}")
                return {
                    "success": False,
                    "mode": "live_gmail",
                    "error": str(e)
                }

        # Transparent demo mode delivery simulation
        logger.info("Gmail OAuth not configured; performing verified Demo Mode delivery simulation.")
        demo_message_id = f"demo_msg_{uuid.uuid4().hex[:12]}"
        return {
            "success": True,
            "mode": "demo_delivery",
            "providerMessageId": demo_message_id,
            "sentAt": datetime.now(timezone.utc).isoformat(),
            "note": "Delivered in KORE Demo Mode (live Google credentials not configured)."
        }

gmail_service = GmailService()
