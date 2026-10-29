"""Test/helper utilities for the M3 email-assistant lab.

Thin wrappers around the simulated email_service endpoints, for manually
sanity-checking the backend before handing control to the LLM.
"""

import json

from IPython.display import HTML, display

import email_service

client = email_service.client


def print_html(content: str, title: str = ""):
    html = f"""
    <div style="border:1px solid #ccc; border-radius:6px; padding:10px; margin:6px 0; background:#fafafa; color:#111;">
      <div style="font-weight:bold; margin-bottom:6px;">{title}</div>
      <pre style="white-space:pre-wrap; margin:0;">{content}</pre>
    </div>
    """
    display(HTML(html))


def reset_database():
    data = client.get("/reset_database").json()
    print_html(json.dumps(data, indent=2, default=str), "reset_database")
    return data


def test_send_email(recipient="test@example.com", subject="Lunch plans", body="Shall we meet at noon?"):
    data = client.post("/send", json={"recipient": recipient, "subject": subject, "body": body}).json()
    print_html(json.dumps(data, indent=2, default=str), "test_send_email")
    return data


def test_get_email(email_id):
    data = client.get(f"/emails/{email_id}").json()
    print_html(json.dumps(data, indent=2, default=str), "test_get_email")
    return data


def test_list_emails():
    data = client.get("/emails").json()
    print_html(json.dumps(data, indent=2, default=str), "test_list_emails")
    return data


def test_filter_emails(recipient=None, date_from=None, date_to=None):
    params = {k: v for k, v in dict(recipient=recipient, date_from=date_from, date_to=date_to).items() if v}
    data = client.get("/emails/filter", params=params).json()
    print_html(json.dumps(data, indent=2, default=str), "test_filter_emails")
    return data


def test_search_emails(query):
    data = client.get("/emails/search", params={"q": query}).json()
    print_html(json.dumps(data, indent=2, default=str), "test_search_emails")
    return data


def test_unread_emails():
    data = client.get("/emails/unread").json()
    print_html(json.dumps(data, indent=2, default=str), "test_unread_emails")
    return data


def test_mark_read(email_id):
    data = client.patch(f"/emails/{email_id}/read").json()
    print_html(json.dumps(data, indent=2, default=str), "test_mark_read")
    return data


def test_mark_unread(email_id):
    data = client.patch(f"/emails/{email_id}/unread").json()
    print_html(json.dumps(data, indent=2, default=str), "test_mark_unread")
    return data


def test_delete_email(email_id):
    data = client.delete(f"/emails/{email_id}").json()
    print_html(json.dumps(data, indent=2, default=str), "test_delete_email")
    return data
