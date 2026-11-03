import os

import mailtrap as mt
from mailtrap.models.attachments import Attachment

API_KEY = os.environ["MAILTRAP_API_KEY"]
ACCOUNT_ID = os.environ["MAILTRAP_ACCOUNT_ID"]
SANDBOX_ID = os.environ["MAILTRAP_SANDBOX_ID"]
MESSAGE_ID = os.environ["MAILTRAP_SANDBOX_MESSAGE_ID"]

client = mt.MailtrapClient(token=API_KEY, account_id=ACCOUNT_ID)
attachments_api = client.sandbox_api.attachments


def list_attachments(sandbox_id: int, message_id: int) -> list[Attachment]:
    return attachments_api.get_list(sandbox_id=sandbox_id, message_id=message_id)


def get_attachment(sandbox_id: int, message_id: int, attachment_id: int) -> Attachment:
    return attachments_api.get(
        sandbox_id=sandbox_id,
        message_id=message_id,
        attachment_id=attachment_id,
    )


if __name__ == "__main__":
    attachments = list_attachments(sandbox_id=SANDBOX_ID, message_id=MESSAGE_ID)
    print(attachments)
    if attachments:
        attachment = get_attachment(
            sandbox_id=SANDBOX_ID, message_id=MESSAGE_ID, attachment_id=attachments[0].id
        )
        print(attachment)
