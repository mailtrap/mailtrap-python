"""Example: List email logs and get a single message by ID."""

from datetime import datetime
from datetime import timedelta
from datetime import timezone

import mailtrap as mt
from mailtrap.models.email_logs import EmailLogsListFilters
from mailtrap.models.email_logs import filter_ci_equal
from mailtrap.models.email_logs import filter_string_equal
from mailtrap.models.email_logs import filter_string_not_empty

API_TOKEN = "YOUR_API_TOKEN"
ACCOUNT_ID = "YOUR_ACCOUNT_ID"

client = mt.MailtrapClient(token=API_TOKEN, account_id=ACCOUNT_ID)
email_logs_api = client.email_logs_api.email_logs


def list_email_logs():
    """List email logs (first page)."""
    return email_logs_api.get_list()


def list_email_logs_with_filters():
    """List email logs from last 2 days, by category(s), with non-empty subject."""
    now = datetime.now(timezone.utc)
    two_days_ago = now - timedelta(days=2)
    filters = EmailLogsListFilters(
        sent_after=two_days_ago.isoformat().replace("+00:00", "Z"),
        sent_before=now.isoformat().replace("+00:00", "Z"),
        subject=filter_string_not_empty(),
        to=filter_ci_equal("recipient@example.com"),
        category=filter_string_equal(["Welcome Email", "Password Reset"]),
    )
    return email_logs_api.get_list(filters=filters)


def get_next_page(previous_response):
    """Fetch next page using cursor from previous response."""
    if previous_response.next_page_cursor is None:
        return None
    return email_logs_api.get_list(search_after=previous_response.next_page_cursor)


def get_message(message_id: str):
    """Get a single email log message by UUID."""
    return email_logs_api.get_by_id(message_id)


if __name__ == "__main__":
    # List first page
    response = list_email_logs()
    print(f"Total: {response.total_count}, messages: {len(response.messages)}")
    for msg in response.messages:
        print(f"  {msg.message_id} | {msg.from_} -> {msg.to} | {msg.status}")

    # Get single message
    if response.messages:
        detail = get_message(response.messages[0].message_id)
        print(f"Detail: {detail.subject}, events: {len(detail.events)}")
