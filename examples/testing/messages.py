from typing import Optional

import mailtrap as mt
from mailtrap.models.messages import AnalysisReport
from mailtrap.models.messages import EmailMessage
from mailtrap.models.messages import ForwardedMessage
from mailtrap.models.messages import SpamReport

API_TOKEN = "YOUR_API_TOKEN"
ACCOUNT_ID = "YOUR_ACCOUNT_ID"
INBOX_ID = "YOUR_INBOX_ID"

client = mt.MailtrapClient(token=API_TOKEN, account_id=ACCOUNT_ID)
messages_api = client.testing_api.messages


def get_message(inbox_id: int, message_id: int) -> EmailMessage:
    return messages_api.show_message(inbox_id=inbox_id, message_id=message_id)


def update_message(inbox_id: int, message_id: int, is_read: bool) -> EmailMessage:
    return messages_api.update(
        inbox_id=inbox_id,
        message_id=message_id,
        message_params=mt.UpdateEmailMessageParams(is_read=is_read),
    )


def delete_message(inbox_id: int, message_id: int) -> EmailMessage:
    return messages_api.delete(inbox_id=inbox_id, message_id=message_id)


def list_messages(
    inbox_id: int,
    search: Optional[str] = None,
    last_id: Optional[int] = None,
    page: Optional[int] = None,
) -> list[EmailMessage]:
    return messages_api.get_list(
        inbox_id=inbox_id, search=search, last_id=last_id, page=page
    )


def forward_message(inbox_id: int, message_id: int, email: str) -> ForwardedMessage:
    return messages_api.forward(inbox_id=inbox_id, message_id=message_id, email=email)


def get_spam_report(inbox_id: int, message_id: str) -> SpamReport:
    return messages_api.get_spam_report(inbox_id=inbox_id, message_id=message_id)


def get_html_analysis(inbox_id: int, message_id: str) -> AnalysisReport:
    return messages_api.get_html_analysis(inbox_id=inbox_id, message_id=message_id)


def get_text_message(inbox_id: int, message_id: str) -> str:
    return messages_api.get_text_message(inbox_id=inbox_id, message_id=message_id)


def get_raw_message(inbox_id: int, message_id: str) -> str:
    return messages_api.get_raw_message(inbox_id=inbox_id, message_id=message_id)


def get_html_source(inbox_id: int, message_id: str) -> str:
    return messages_api.get_html_source(inbox_id=inbox_id, message_id=message_id)


def get_html_message(inbox_id: int, message_id: str) -> str:
    return messages_api.get_html_message(inbox_id=inbox_id, message_id=message_id)


def get_message_as_eml(inbox_id: int, message_id: str) -> str:
    return messages_api.get_message_as_eml(inbox_id=inbox_id, message_id=message_id)


def get_mail_headers(inbox_id: int, message_id: str) -> str:
    return messages_api.get_mail_headers(inbox_id=inbox_id, message_id=message_id)


if __name__ == "__main__":
    messages = list_messages(inbox_id=INBOX_ID)
    print(messages)
    if messages:
        msg_id = messages[0].id
        message = get_message(inbox_id=INBOX_ID, message_id=msg_id)
        print(message)

        updated = update_message(inbox_id=INBOX_ID, message_id=msg_id, is_read=True)
        print(updated)

        forwarded = forward_message(
            inbox_id=INBOX_ID,
            message_id=msg_id,
            email="example@example.com",
        )
        print(forwarded)

        spam = get_spam_report(inbox_id=INBOX_ID, message_id=msg_id)
        print(spam)

        html_analysis = get_html_analysis(inbox_id=INBOX_ID, message_id=msg_id)
        print(html_analysis)

        text = get_text_message(inbox_id=INBOX_ID, message_id=msg_id)
        print(text)

        raw = get_raw_message(inbox_id=INBOX_ID, message_id=msg_id)
        print(raw)

        html_src = get_html_source(inbox_id=INBOX_ID, message_id=msg_id)
        print(html_src)

        html_msg = get_html_message(inbox_id=INBOX_ID, message_id=msg_id)
        print(html_msg)

        eml = get_message_as_eml(inbox_id=INBOX_ID, message_id=msg_id)
        print(eml)

        headers = get_mail_headers(inbox_id=INBOX_ID, message_id=msg_id)
        print(headers)
