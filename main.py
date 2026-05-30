import concurrent.futures
import json
import os

import config
from tools.email_tools import load_emails_tool
from agents.email_agent import EmailAgent


def reset_output_files():
    """Clear sent_mails.json and report.json before each run."""
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    for filename in ['sent_mails.json', 'report.json']:
        path = os.path.join(data_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump([], f)


def print_report(results):
    """Print the final categorized report to the console."""
    groups = {
        'decision_required': [],
        'auto_reply_possible': [],
        'notification_only': [],
        'no_response_needed': [],
        'spam': [],
    }
    for result in results:
        groups[result['category']].append(result)

    print("\n" + "=" * 55)
    print("           EMAIL PROCESSING REPORT")
    print("=" * 55)

    if groups['decision_required']:
        print("\n[Decision Required]")
        for r in groups['decision_required']:
            if r.get('detail') == 'schedule_conflict':
                print(f"  - 일정 충돌: {r['from']}의 회의 요청이 기존 일정과 충돌합니다.")
            else:
                print(f"  - 의사결정 필요: {r['from']}의 메일은 사용자의 선택이 필요합니다.")

    if groups['auto_reply_possible']:
        print("\n[Auto Replied]")
        for r in groups['auto_reply_possible']:
            print(f"  - {r['from']}에게 자동 답장을 저장했습니다.")

    if groups['notification_only']:
        print("\n[Notification Only]")
        for r in groups['notification_only']:
            print(f"  - {r['from']}의 {r['subject']} 메일을 확인했습니다.")

    if groups['no_response_needed']:
        print("\n[No Response Needed]")
        for r in groups['no_response_needed']:
            print(f"  - {r['from']}의 메일은 응답이 필요 없습니다.")

    if groups['spam']:
        print("\n[Spam]")
        for r in groups['spam']:
            if r.get('action') == 'identified_as_known_spam':
                print(f"  - {r['from']}은 기존 스팸 발신자입니다.")
            else:
                print(f"  - {r['from']}을 신규 스팸 발신자로 등록했습니다.")

    print("\n" + "=" * 55)
    print(f"  Total processed: {len(results)} emails")
    print("=" * 55 + "\n")


def main():
    print("[System] Resetting output files...")
    reset_output_files()

    print(f"[System] Loading emails from source: '{config.EMAIL_SOURCE}'...")
    emails = load_emails_tool()
    print(f"[System] {len(emails)} emails loaded. Starting parallel processing...\n")

    # One agent per email
    agents = [EmailAgent(f"Agent-{i + 1}") for i in range(len(emails))]

    results = []

    # Parallel processing: each agent handles one email concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(agent.process_email, email): agent.agent_id
            for agent, email in zip(agents, emails)
        }
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    # Sort for consistent output order
    results.sort(key=lambda r: r['mail_id'])

    print_report(results)


if __name__ == '__main__':
    main()
