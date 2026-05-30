import json
import os
from tools.file_lock import file_lock

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
REPORT_FILE = os.path.join(DATA_DIR, 'report.json')


def save_report_tool(result):
    """Append a processing result to the report file."""
    with file_lock:
        with open(REPORT_FILE, 'r', encoding='utf-8') as f:
            report = json.load(f)
        report.append(result)
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
