import json
import os
from tools.file_lock import file_lock

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
SPAM_FILE = os.path.join(DATA_DIR, 'spam_senders.json')


def check_spam_sender_tool(sender):
    """Return True if the sender is in the known spam list."""
    with file_lock:
        with open(SPAM_FILE, 'r', encoding='utf-8') as f:
            spam_list = json.load(f)
    return sender in spam_list


def add_spam_sender_tool(sender):
    """Add a new sender to the spam list if not already present."""
    with file_lock:
        with open(SPAM_FILE, 'r', encoding='utf-8') as f:
            spam_list = json.load(f)
        if sender not in spam_list:
            spam_list.append(sender)
            with open(SPAM_FILE, 'w', encoding='utf-8') as f:
                json.dump(spam_list, f, ensure_ascii=False, indent=2)
