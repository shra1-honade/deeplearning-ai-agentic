"""LLM-facing tools for the email assistant agent.

Each function wraps one email_service endpoint. Docstrings follow the
Google Args style aisuite's schema builder expects, so these can be
handed straight to `tools=[...]` in an aisuite chat completion call.
"""

import email_service

client = email_service.client


def list_all_emails():
    """List all emails in the inbox, newest first."""
    return client.get("/emails").json()


def list_unread_emails():
    """Retrieve only the unread emails in the inbox."""
    return client.get("/emails/unread").json()


def search_emails(query: str):
    """Search emails by keyword in the subject, body, or sender.

    Args:
        query: The keyword or phrase to search for.
    """
    return client.get("/emails/search", params={"q": query}).json()


def filter_emails(recipient: str = None, date_from: str = None, date_to: str = None):
    """Filter emails by recipient and/or a date range.

    Args:
        recipient: Only return emails addressed to this recipient.
        date_from: Only return emails on/after this ISO date (YYYY-MM-DD).
        date_to: Only return emails on/before this ISO date (YYYY-MM-DD).
    """
    params = {k: v for k, v in dict(recipient=recipient, date_from=date_from, date_to=date_to).items() if v}
    return client.get("/emails/filter", params=params).json()


def get_email(email_id: int):
    """Fetch a specific email by its ID.

    Args:
        email_id: The ID of the email to fetch.
    """
    return client.get(f"/emails/{email_id}").json()


def mark_email_as_read(email_id: int):
    """Mark an email as read.

    Args:
        email_id: The ID of the email to mark as read.
    """
    return client.patch(f"/emails/{email_id}/read").json()


def mark_email_as_unread(email_id: int):
    """Mark an email as unread.

    Args:
        email_id: The ID of the email to mark as unread.
    """
    return client.patch(f"/emails/{email_id}/unread").json()


def send_email(recipient: str, subject: str, body: str):
    """Send a new email from the user's own account.

    Args:
        recipient: The email address to send the message to.
        subject: The subject line of the email.
        body: The body text of the email.
    """
    return client.post("/send", json={"recipient": recipient, "subject": subject, "body": body}).json()


def delete_email(email_id: int):
    """Permanently delete an email by its ID.

    Args:
        email_id: The ID of the email to delete.
    """
    return client.delete(f"/emails/{email_id}").json()


def search_unread_from_sender(sender_address: str):
    """Return unread emails from a specific sender address.

    Args:
        sender_address: The email address of the sender to search for.
    """
    emails = client.get("/emails/unread").json()
    return [e for e in emails if e.get("sender", "").lower() == sender_address.lower()]
