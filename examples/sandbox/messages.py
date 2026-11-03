import os
from typing import Any
from typing import Optional

import mailtrap as mt
from mailtrap.models.messages import AnalysisReport
from mailtrap.models.messages import EmailMessage
from mailtrap.models.messages import ForwardedMessage
from mailtrap.models.messages import SpamReport

API_KEY = os.environ["MAILTRAP_API_KEY"]
ACCOUNT_ID = os.environ["MAILTRAP_ACCOUNT_ID"]
SANDBOX_ID = os.environ["MAILTRAP_SANDBOX_ID"]

client = mt.MailtrapClient(token=API_KEY, account_id=ACCOUNT_ID)
messages_api = client.sandbox_api.messages


def get_message(sandbox_id: int, message_id: int) -> EmailMessage:
    return messages_api.show_message(sandbox_id=sandbox_id, message_id=message_id)


def update_message(sandbox_id: int, message_id: int, is_read: bool) -> EmailMessage:
    return messages_api.update(
        sandbox_id=sandbox_id,
        message_id=message_id,
        message_params=mt.UpdateEmailMessageParams(is_read=is_read),
    )


def delete_message(sandbox_id: int, message_id: int) -> EmailMessage:
    return messages_api.delete(sandbox_id=sandbox_id, message_id=message_id)


def list_messages(
    sandbox_id: int,
    search: Optional[str] = None,
    last_id: Optional[int] = None,
    page: Optional[int] = None,
) -> list[EmailMessage]:
    return messages_api.get_list(
        sandbox_id=sandbox_id, search=search, last_id=last_id, page=page
    )


def forward_message(sandbox_id: int, message_id: int, email: str) -> ForwardedMessage:
    return messages_api.forward(sandbox_id=sandbox_id, message_id=message_id, email=email)


def get_spam_report(sandbox_id: int, message_id: str) -> SpamReport:
    return messages_api.get_spam_report(sandbox_id=sandbox_id, message_id=message_id)


def get_html_analysis(sandbox_id: int, message_id: str) -> AnalysisReport:
    return messages_api.get_html_analysis(sandbox_id=sandbox_id, message_id=message_id)


def get_text_message(sandbox_id: int, message_id: str) -> str:
    return messages_api.get_text_message(sandbox_id=sandbox_id, message_id=message_id)


def get_raw_message(sandbox_id: int, message_id: str) -> str:
    return messages_api.get_raw_message(sandbox_id=sandbox_id, message_id=message_id)


def get_html_source(sandbox_id: int, message_id: str) -> str:
    return messages_api.get_html_source(sandbox_id=sandbox_id, message_id=message_id)


def get_html_message(sandbox_id: int, message_id: str) -> str:
    return messages_api.get_html_message(sandbox_id=sandbox_id, message_id=message_id)


def get_message_as_eml(sandbox_id: int, message_id: str) -> str:
    return messages_api.get_message_as_eml(sandbox_id=sandbox_id, message_id=message_id)


def get_mail_headers(sandbox_id: int, message_id: str) -> dict[str, Any]:
    return messages_api.get_mail_headers(sandbox_id=sandbox_id, message_id=message_id)


if __name__ == "__main__":
    messages = list_messages(sandbox_id=SANDBOX_ID)
    print(messages)
    if messages:
        msg_id = messages[0].id
        message = get_message(sandbox_id=SANDBOX_ID, message_id=msg_id)
        print(message)

        updated = update_message(sandbox_id=SANDBOX_ID, message_id=msg_id, is_read=True)
        print(updated)

        forwarded = forward_message(
            sandbox_id=SANDBOX_ID,
            message_id=msg_id,
            email="example@example.com",
        )
        print(forwarded)

        spam = get_spam_report(sandbox_id=SANDBOX_ID, message_id=msg_id)
        print(spam)

        html_analysis = get_html_analysis(sandbox_id=SANDBOX_ID, message_id=msg_id)
        print(html_analysis)

        text = get_text_message(sandbox_id=SANDBOX_ID, message_id=msg_id)
        print(text)

        raw = get_raw_message(sandbox_id=SANDBOX_ID, message_id=msg_id)
        print(raw)

        html_src = get_html_source(sandbox_id=SANDBOX_ID, message_id=msg_id)
        print(html_src)

        html_msg = get_html_message(sandbox_id=SANDBOX_ID, message_id=msg_id)
        print(html_msg)

        eml = get_message_as_eml(sandbox_id=SANDBOX_ID, message_id=msg_id)
        print(eml)

        headers = get_mail_headers(sandbox_id=SANDBOX_ID, message_id=msg_id)
        print(headers)
