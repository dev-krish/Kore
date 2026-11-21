from typing import Any, Dict, Optional
from app.engine.tools.base import BaseTool, ToolResult
from app.models.draft import EmailDraftModel, ApprovalStatus
from app.services.email.approval_gate import approval_gate
from app.services.email.gmail_service import gmail_service

class SendEmailTool(BaseTool):
    name = "send_email"
    description = (
        "Sends an approved email draft via Gmail API. "
        "CRITICAL: This tool strictly enforces human approval. It rejects execution unless "
        "the draft was explicitly approved by the user and matches the exact content hash."
    )

    async def execute(
        self,
        draft: Dict[str, Any],
        user_tokens: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> ToolResult:
        try:
            draft_model = EmailDraftModel(**draft)
            
            # Step 1: Validate through Approval Gate
            is_valid, reason = approval_gate.verify_ready_for_sending(draft_model)
            if not is_valid:
                return ToolResult(
                    success=False,
                    error=f"HUMAN APPROVAL GATE BLOCKED: {reason}"
                )

            # Step 2: Send email via Gmail service
            result = await gmail_service.send_email(
                recipient=draft_model.recipientEmail,
                subject=draft_model.subject,
                body=draft_model.body,
                user_tokens=user_tokens
            )

            if not result.get("success"):
                return ToolResult(
                    success=False,
                    error=f"Delivery failure: {result.get('error', 'Unknown error')}"
                )

            return ToolResult(
                success=True,
                data=result,
                source_attribution="Gmail API delivery log"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Send email tool exception: {str(e)}"
            )
