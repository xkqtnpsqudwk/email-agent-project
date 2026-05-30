"""
Global configuration for the email processing system.

Switch EMAIL_SOURCE between "dummy" and "gmail":
  - "dummy": load emails from data/dummy_mails.json (no API key needed)
  - "gmail": load emails from a real Gmail account via the Gmail API
             (requires google-api-python-client + OAuth credentials)
"""

EMAIL_SOURCE = "dummy"  # change to "gmail" to use the real Gmail API

# Gmail API settings (only used when EMAIL_SOURCE == "gmail")
GMAIL_MAX_RESULTS = 10
GMAIL_QUERY = "is:unread"  # Gmail search query, e.g. "is:unread in:inbox"

# OAuth file paths (these are git-ignored, see .gitignore)
GMAIL_CREDENTIALS_FILE = "data/credentials.json"  # downloaded from Google Cloud Console
GMAIL_TOKEN_FILE = "data/token.json"              # auto-generated after first login
