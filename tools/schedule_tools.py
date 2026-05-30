import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
SCHEDULE_FILE = os.path.join(DATA_DIR, 'schedule.json')


def check_schedule_conflict_tool(start_time_str, end_time_str):
    """Return True if the given time range overlaps with any existing schedule entry."""
    with open(SCHEDULE_FILE, 'r', encoding='utf-8') as f:
        schedules = json.load(f)

    new_start = datetime.fromisoformat(start_time_str)
    new_end = datetime.fromisoformat(end_time_str)

    for event in schedules:
        existing_start = datetime.fromisoformat(event['start_time'])
        existing_end = datetime.fromisoformat(event['end_time'])
        # Overlap: new event starts before existing ends AND ends after existing starts
        if new_start < existing_end and new_end > existing_start:
            return True

    return False
