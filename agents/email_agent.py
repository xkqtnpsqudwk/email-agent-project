from tools.email_tools import normalize_email_tool
from tools.spam_tools import check_spam_sender_tool, add_spam_sender_tool
from tools.schedule_tools import check_schedule_conflict_tool
from tools.reply_tools import save_sent_reply_tool
from tools.report_tools import save_report_tool

# Rule-based keyword lists for email classification
SPAM_KEYWORDS = [
    'click here', 'winner', 'prize', 'claim now',
    'verify your credentials', 'compromised', 'phishing', 'urgent',
]

DECISION_KEYWORDS = [
    'please choose', 'select one', 'your decision', 'approval required',
    'which option', 'option a', 'option b',
]

NOTIFICATION_KEYWORDS = [
    'completed', 'maintenance', 'notify', 'notification',
    'announcement', 'fyi', 'all systems',
]

AUTO_REPLY_KEYWORDS = [
    'did you receive', 'please confirm', 'can you confirm',
    'quick question', 'just checking', 'acknowledge receipt',
]


class EmailAgent:
    """
    An agent that processes a single email by classifying it and calling
    the appropriate tools based on the classification result.
    """

    def __init__(self, agent_id):
        self.agent_id = agent_id

    def _log(self, tool_name):
        print(f"[{self.agent_id}] call tool: {tool_name}")

    def _classify(self, email):
        """
        Rule-based classifier. Returns (category, detail).
        Categories: spam, decision_required, notification_only,
                    auto_reply_possible, no_response_needed
        """
        sender = email['from']
        text = (email['subject'] + ' ' + email['body']).lower()

        # 1. Check known spam sender
        self._log('check_spam_sender_tool')
        if check_spam_sender_tool(sender):
            return 'spam', 'known'

        # 2. Check spam keywords in subject/body
        for keyword in SPAM_KEYWORDS:
            if keyword in text:
                return 'spam', 'new'

        # 3. Check for schedule conflict if time fields exist
        if email.get('start_time') and email.get('end_time'):
            self._log('check_schedule_conflict_tool')
            if check_schedule_conflict_tool(email['start_time'], email['end_time']):
                return 'decision_required', 'schedule_conflict'

        # 4. Check for decision-required keywords
        for keyword in DECISION_KEYWORDS:
            if keyword in text:
                return 'decision_required', 'user_choice'

        # 5. Check for notification keywords
        for keyword in NOTIFICATION_KEYWORDS:
            if keyword in text:
                return 'notification_only', None

        # 6. Check for auto-reply keywords
        for keyword in AUTO_REPLY_KEYWORDS:
            if keyword in text:
                return 'auto_reply_possible', None

        return 'no_response_needed', None

    def _generate_reply(self, email):
        return (
            f"Hi,\n\n"
            f"Thank you for your email regarding '{email['subject']}'. "
            f"I have received your message and will follow up if needed.\n\n"
            f"Best regards,\nAuto-Reply System"
        )

    def process_email(self, email):
        """
        Main entry point: normalize -> classify -> execute appropriate tools.
        Returns a result dict that will be saved to the report.
        """
        self._log('normalize_email_tool')
        email = normalize_email_tool(email)

        category, detail = self._classify(email)

        result = {
            'mail_id': email['id'],
            'from': email['from'],
            'subject': email['subject'],
            'category': category,
            'detail': detail,
            'agent': self.agent_id,
        }

        if category == 'spam' and detail == 'new':
            self._log('add_spam_sender_tool')
            add_spam_sender_tool(email['from'])
            result['action'] = 'registered_as_new_spam'

        elif category == 'spam':
            result['action'] = 'identified_as_known_spam'

        elif category == 'auto_reply_possible':
            self._log('save_sent_reply_tool')
            save_sent_reply_tool(email, self._generate_reply(email))
            result['action'] = 'auto_reply_sent'

        self._log('save_report_tool')
        save_report_tool(result)

        return result
