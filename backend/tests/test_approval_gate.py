import pytest
from app.models.draft import ApprovalStatus, EmailDraftModel
from app.services.email.approval_gate import approval_gate

def test_approval_gate_blocks_unapproved_draft():
    draft = EmailDraftModel(
        userId="user1",
        campaignId="camp1",
        contactId="ct1",
        companyId="comp1",
        recipientName="Alice",
        recipientEmail="alice@startup.io",
        recipientRole="CTO",
        companyName="Startup",
        subject="Internship Inquiry",
        body="Dear Alice, I would love to join your engineering team.",
        approvalStatus=ApprovalStatus.GENERATED,
        approvedContentHash=None
    )
    is_valid, reason = approval_gate.verify_ready_for_sending(draft)
    assert is_valid is False
    assert "not 'approved'" in reason

def test_approval_gate_verifies_valid_hash():
    recipient = "alice@startup.io"
    subject = "Internship Inquiry"
    body = "Dear Alice, I would love to join your engineering team."
    valid_hash = approval_gate.compute_content_hash(recipient, subject, body)

    draft = EmailDraftModel(
        userId="user1",
        campaignId="camp1",
        contactId="ct1",
        companyId="comp1",
        recipientName="Alice",
        recipientEmail=recipient,
        recipientRole="CTO",
        companyName="Startup",
        subject=subject,
        body=body,
        approvalStatus=ApprovalStatus.APPROVED,
        approvedContentHash=valid_hash
    )
    is_valid, reason = approval_gate.verify_ready_for_sending(draft)
    assert is_valid is True

def test_approval_gate_blocks_modified_content_tampering():
    recipient = "alice@startup.io"
    subject = "Original Subject"
    body = "Original Body"
    original_hash = approval_gate.compute_content_hash(recipient, subject, body)

    # Content altered after approval
    draft = EmailDraftModel(
        userId="user1",
        campaignId="camp1",
        contactId="ct1",
        companyId="comp1",
        recipientName="Alice",
        recipientEmail=recipient,
        recipientRole="CTO",
        companyName="Startup",
        subject="TAMPERED Subject",
        body=body,
        approvalStatus=ApprovalStatus.APPROVED,
        approvedContentHash=original_hash
    )
    is_valid, reason = approval_gate.verify_ready_for_sending(draft)
    assert is_valid is False
    assert "integrity mismatch" in reason
