from typing import Optional

import mailtrap as mt
from mailtrap.models.inboxes import Inbox

API_TOKEN = "YOUR_API_TOKEN"
ACCOUNT_ID = "YOUR_ACCOUNT_ID"

client = mt.MailtrapClient(token=API_TOKEN, account_id=ACCOUNT_ID)
inboxes_api = client.testing_api.inboxes


def list_inboxes() -> list[Inbox]:
    return inboxes_api.get_list()


def create_inbox(project_id: int, inbox_name: str) -> Inbox:
    return inboxes_api.create(
        project_id=project_id, inbox_params=mt.CreateInboxParams(name=inbox_name)
    )


def get_inbox_by_id(inbox_id: int) -> Inbox:
    return inboxes_api.get_by_id(inbox_id)


def update_inbox(
    inbox_id: int,
    new_name: Optional[str] = None,
    new_email_username: Optional[str] = None,
) -> Inbox:
    return inboxes_api.update(
        inbox_id, mt.UpdateInboxParams(name=new_name, email_username=new_email_username)
    )


def clean_inbox(inbox_id: int) -> Inbox:
    return inboxes_api.clean(inbox_id)


def mark_inbox_as_read(inbox_id: int) -> Inbox:
    return inboxes_api.mark_as_read(inbox_id)


def reset_inbox_credentials(inbox_id: int) -> Inbox:
    return inboxes_api.reset_credentials(inbox_id)


def enable_inbox_email_address(inbox_id: int) -> Inbox:
    return inboxes_api.enable_email_address(inbox_id)


def reset_inbox_email_username(inbox_id: int) -> Inbox:
    return inboxes_api.reset_email_username(inbox_id)


def delete_inbox(inbox_id: int):
    return inboxes_api.delete(inbox_id)


if __name__ == "__main__":
    created = create_inbox(project_id=1, inbox_name="example-created-inbox")
    print(created)

    inboxes = list_inboxes()
    print(inboxes)

    inbox_id = inboxes[0].id
    inbox = get_inbox_by_id(inbox_id=inbox_id)
    print(inbox)

    updated = update_inbox(inbox_id=inbox_id, new_name=f"{inbox.name}-updated")
    print(updated)

    cleaned = clean_inbox(inbox_id=inbox_id)
    print(cleaned)

    marked = mark_inbox_as_read(inbox_id=inbox_id)
    print(marked)

    reset_creds = reset_inbox_credentials(inbox_id=inbox_id)
    print(reset_creds)

    enabled = enable_inbox_email_address(inbox_id=inbox_id)
    print(enabled)

    reset_username = reset_inbox_email_username(inbox_id=inbox_id)
    print(reset_username)

    deleted = delete_inbox(inbox_id=inbox_id)
    print(deleted)
