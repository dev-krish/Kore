import base64
from email.mime.text import MIMEText
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple
from app.core.config import settings

logger = logging.getLogger(__name__)

class GmailService:
    """
    Gmail OAuth 2.0 and API integration service.
    Implements authorization code exchange, token refresh, and sending emails
    with strict user-scoped credential checks.
    """

    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI

    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret)

    def get_auth_url(self, state: str) -> str:
        if not self.is_configured():
            return f"{settings.FRONTEND_URL}/integrations?demo_gmail=configured&state={state}"
        
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
        auth_url, _ = flow.authorization_url(state=state, prompt="consent", access_type="offline")
        return auth_url

    def exchange_code(self, code: str) -> Dict[str, Any]:
        """
        Exchanges an OAuth authorization code for Google user credentials.
        """
        if not self.is_configured():
            # In demo mode, return simulated credentials format
            return {
                "access_token": f"demo_access_token_{uuid.uuid4().hex[:16]}",
                "refresh_token": f"demo_refresh_token_{uuid.uuid4().hex[:16]}",
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": "demo_client_id",
                "scopes": ["https://www.googleapis.com/auth/gmail.send"],
                "expires_at": None,
                "is_demo_token": True
            }

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
        flow.fetch_token(code=code)
        credentials = flow.credentials

        return {
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes,
            "expiry": credentials.expiry.isoformat() if credentials.expiry else None,
            "is_demo_token": False
        }

    async def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
        user_tokens: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        logger.info(f"Gmail send request initiated for recipient: {recipient}")

        # Check for live Google credentials and valid user token
        if self.is_configured() and user_tokens and user_tokens.get("access_token") and not user_tokens.get("is_demo_token"):
            try:
                from google.oauth2.credentials import Credentials
                from google.auth.transport.requests import Request
                from googleapiclient.discovery import build

                creds = Credentials(
                    token=user_tokens.get("access_token"),
                    refresh_token=user_tokens.get("refresh_token"),
                    token_uri=user_tokens.get("token_uri", "https://oauth2.googleapis.com/token"),
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    scopes=user_tokens.get("scopes", ["https://www.googleapis.com/auth/gmail.send"])
                )

                # Token refresh handling if expired
                if creds.expired and creds.refresh_token:
                    logger.info("Access token expired. Refreshing token via Google OAuth...")
                    creds.refresh(Request())
                    # Note: caller should update the stored token

                service = build("gmail", "v1", credentials=creds)

                message = MIMEText(body)
                message["to"] = recipient
                message["subject"] = subject
                raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

                sent_msg = service.users().messages().send(
                    userId="me",
                    body={"raw": raw_message}
                ).execute()

                logger.info(f"Email sent via live Gmail API! Message ID: {sent_msg.get('id')}")
                return {
                    "success": True,
                    "mode": "live_gmail",
                    "providerMessageId": sent_msg.get("id"),
                    "sentAt": datetime.now(timezone.utc).isoformat(),
                    "refreshedToken": creds.token if creds.expired else None
                }
            except Exception as e:
                logger.error(f"Live Gmail API delivery failed: {e}")
                return {
                    "success": False,
                    "mode": "live_gmail",
                    "error": str(e)
                }

        # If live credentials are required but user has not connected Gmail
        if self.is_configured() and not user_tokens:
            return {
                "success": False,
                "mode": "live_gmail",
                "error": "Gmail account not connected. Please connect your Gmail account in Integrations before sending."
            }

        # Explicit demo delivery simulation
        if settings.GMAIL_MODE == "demo" or not self.is_configured() or (user_tokens and user_tokens.get("is_demo_token")):
            logger.info("Executing simulated demo delivery (OAuth not configured or demo mode selected).")
            demo_message_id = f"demo_msg_{uuid.uuid4().hex[:12]}"
            return {
                "success": True,
                "mode": "demo_delivery",
                "providerMessageId": demo_message_id,
                "sentAt": datetime.now(timezone.utc).isoformat(),
                "note": "Delivered in KORE Demo Mode (live Google OAuth not configured or in demo mode)."
            }

        return {
            "success": False,
            "mode": "live_gmail",
            "error": "Gmail integration is not operational. Please check Google OAuth credentials."
        }

gmail_service = GmailService()
