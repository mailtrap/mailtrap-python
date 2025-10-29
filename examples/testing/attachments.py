import mailtrap as mt
from mailtrap.models.attachments import Attachment

API_TOKEN = "YOUR_API_TOKEN"
ACCOUNT_ID = "YOUR_ACCOUNT_ID"
INBOX_ID = "YOUR_INBOX_ID"
MESSAGE_ID = "YOUR_MESSAGE_ID"

client = mt.MailtrapClient(token=API_TOKEN, account_id=ACCOUNT_ID)
attachments_api = client.testing_api.attachments


def list_attachments(inbox_id: int, message_id: int) -> list[Attachment]:
    return attachments_api.get_list(inbox_id=inbox_id, message_id=message_id)


def get_attachment(inbox_id: int, message_id: int, attachment_id: int) -> Attachment:
    return attachments_api.get(
        inbox_id=inbox_id,
        message_id=message_id,
        attachment_id=attachment_id,
    )


if __name__ == "__main__":
    attachments = list_attachments(inbox_id=INBOX_ID, message_id=MESSAGE_ID)
    print(attachments)
    if attachments:
        attachment = get_attachment(
            inbox_id=INBOX_ID, message_id=MESSAGE_ID, attachment_id=attachments[0].id
        )
        print(attachment)
