import json
import os
from tools.file_lock import file_lock

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
SENT_FILE = os.path.join(DATA_DIR, 'sent_mails.json')


def save_sent_reply_tool(email, reply_text):
    """Append an auto-reply record to the sent mails file."""
    entry = {
        'original_mail_id': email['id'],
        'to': email['from'],
        'subject': f"Re: {email['subject']}",
        'body': reply_text,
    }
    with file_lock:
        with open(SENT_FILE, 'r', encoding='utf-8') as f:
            sent_mails = json.load(f)
        sent_mails.append(entry)
        with open(SENT_FILE, 'w', encoding='utf-8') as f:
            json.dump(sent_mails, f, ensure_ascii=False, indent=2)
    return entry
