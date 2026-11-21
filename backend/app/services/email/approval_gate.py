import hashlib
import logging
from typing import Dict, Any, Tuple
from app.models.draft import ApprovalStatus, EmailDraftModel

logger = logging.getLogger(__name__)

class ApprovalGate:
    """
    Strict Human-in-the-Loop Approval Gate.
    Guarantees:
    1. An email can NEVER be sent without explicit prior human approval.
    2. Approval is bound to the exact content hash of recipient + subject + body.
    3. Any edit to subject or body invalidates existing approval.
    4. Duplicate sends are strictly blocked.
    """

    @staticmethod
    def compute_content_hash(recipient: str, subject: str, body: str) -> str:
        canonical = f"{recipient.strip().lower()}||{subject.strip()}||{body.strip()}"
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @staticmethod
    def verify_ready_for_sending(draft: EmailDraftModel) -> Tuple[bool, str]:
        # 1. Status check
        if draft.approvalStatus != ApprovalStatus.APPROVED:
            return False, f"Sending rejected: Draft status is '{draft.approvalStatus}', not '{ApprovalStatus.APPROVED.value}'."

        # 2. Already sent check
        if draft.approvalStatus == ApprovalStatus.SENT:
            return False, "Sending rejected: This email draft has already been sent."

        # 3. Content hash check
        if not draft.approvedContentHash:
            return False, "Sending rejected: No cryptographic approval hash found on draft."

        current_hash = ApprovalGate.compute_content_hash(
            recipient=draft.recipientEmail,
            subject=draft.subject,
            body=draft.body
        )

        if current_hash != draft.approvedContentHash:
            return False, (
                "Sending rejected: Content integrity mismatch! The subject or body was modified after approval. "
                "Draft approval has been invalidated. Please review and approve again."
            )

        return True, "Approval gate verified successfully."

approval_gate = ApprovalGate()
