import json
import os

import config

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')


def _load_emails_from_dummy():
    """Load all emails from the dummy mail file."""
    path = os.path.join(DATA_DIR, 'dummy_mails.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_emails_tool():
    """
    Load emails from the configured source.

    The source is chosen in config.py via EMAIL_SOURCE:
      - "dummy": read data/dummy_mails.json (default, no API key needed)
      - "gmail": fetch from a real Gmail account via the Gmail API

    Both sources return the same list-of-dicts format, so the agents and
    other tools work without any changes regardless of the source.
    """
    if config.EMAIL_SOURCE == 'gmail':
        # Imported lazily so the project still runs in dummy mode even if
        # the Google API libraries are not installed.
        from tools.gmail_tools import load_emails_from_gmail
        return load_emails_from_gmail()
    return _load_emails_from_dummy()


def normalize_email_tool(email):
    """Normalize email fields and ensure consistent structure."""
    return {
        'id': email.get('id', 'unknown'),
        'from': email.get('from', '').strip().lower(),
        'subject': email.get('subject', '').strip(),
        'body': email.get('body', '').strip(),
        'start_time': email.get('start_time'),
        'end_time': email.get('end_time'),
    }
