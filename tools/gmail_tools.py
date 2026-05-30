"""
Gmail API integration.

This module fetches real emails from a Gmail account and converts them into
the SAME dictionary format used by the dummy loader, so the agents and other
tools do not need any changes.

NOTE: This requires extra packages and OAuth credentials. If they are missing,
load_emails_from_gmail() raises a clear error explaining what to install/setup.
Without an API key the rest of the project still runs in "dummy" mode.

Setup steps (when you actually want to use Gmail):
  1. pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
  2. Create an OAuth 2.0 Client ID (Desktop app) in Google Cloud Console.
  3. Enable the Gmail API for your project.
  4. Download the credentials and save them as data/credentials.json
  5. Set EMAIL_SOURCE = "gmail" in config.py and run main.py.
     A browser window opens for login; a token is saved to data/token.json.
"""

import base64
import os

import config

# Read-only access is enough: we only list and read messages.
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")


def _get_gmail_service():
    """Authenticate with OAuth and return a Gmail API service object."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError as exc:
        raise RuntimeError(
            "Gmail API libraries are not installed. Run:\n"
            "  pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
        ) from exc

    token_path = os.path.join(PROJECT_ROOT, config.GMAIL_TOKEN_FILE)
    creds_path = os.path.join(PROJECT_ROOT, config.GMAIL_CREDENTIALS_FILE)

    creds = None
    # Reuse a saved token if it exists.
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, GMAIL_SCOPES)

    # Otherwise log in (or refresh an expired token).
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(creds_path):
                raise RuntimeError(
                    f"Missing OAuth credentials file: {creds_path}\n"
                    "Download it from Google Cloud Console (OAuth Client ID, Desktop app)."
                )
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, GMAIL_SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the token for next time.
        with open(token_path, "w", encoding="utf-8") as token_file:
            token_file.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def _get_header(headers, name):
    """Find a header value by name (case-insensitive)."""
    for header in headers:
        if header.get("name", "").lower() == name.lower():
            return header.get("value", "")
    return ""


def _extract_body(payload):
    """Extract the plain-text body from a Gmail message payload."""
    # Simple message: body is directly in the payload.
    data = payload.get("body", {}).get("data")
    if data:
        return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

    # Multipart message: look for the text/plain part.
    for part in payload.get("parts", []):
        if part.get("mimeType") == "text/plain":
            part_data = part.get("body", {}).get("data")
            if part_data:
                return base64.urlsafe_b64decode(part_data).decode("utf-8", errors="replace")

    return ""


def load_emails_from_gmail():
    """
    Fetch emails from Gmail and return them in the project's email format:
      {id, from, subject, body, start_time, end_time}

    start_time/end_time are set to None because parsing meeting times out of
    free-text email bodies is out of scope (same as the dummy data note).
    """
    service = _get_gmail_service()

    response = service.users().messages().list(
        userId="me",
        q=config.GMAIL_QUERY,
        maxResults=config.GMAIL_MAX_RESULTS,
    ).execute()

    message_ids = response.get("messages", [])
    emails = []

    for message_ref in message_ids:
        message = service.users().messages().get(
            userId="me",
            id=message_ref["id"],
            format="full",
        ).execute()

        payload = message.get("payload", {})
        headers = payload.get("headers", [])

        emails.append({
            "id": message["id"],
            "from": _get_header(headers, "From"),
            "subject": _get_header(headers, "Subject"),
            "body": _extract_body(payload),
            "start_time": None,
            "end_time": None,
        })

    return emails
