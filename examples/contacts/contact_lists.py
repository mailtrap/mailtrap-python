import mailtrap as mt
from mailtrap.models.common import DeletedObject
from mailtrap.models.contacts import ContactList

API_TOKEN = "YOUR_API_TOKEN"
ACCOUNT_ID = "YOUR_ACCOUNT_ID"

client = mt.MailtrapClient(token=API_TOKEN, account_id=ACCOUNT_ID)
contact_lists_api = client.contacts_api.contact_lists


def create_contact_list(name: str) -> ContactList:
    params = mt.ContactListParams(name=name)
    return contact_lists_api.create(params)


def update_contact_list(contact_list_id: int, name: str) -> ContactList:
    params = mt.ContactListParams(name=name)
    return contact_lists_api.update(contact_list_id, params)


def list_contact_lists() -> list[ContactList]:
    return contact_lists_api.get_list()


def get_contact_list(contact_list_id: int) -> ContactList:
    return contact_lists_api.get_by_id(contact_list_id)


def delete_contact_list(contact_list_id: int) -> DeletedObject:
    return contact_lists_api.delete(contact_list_id)


if __name__ == "__main__":
    created = create_contact_list(name="example-list")
    print(created)

    lists = list_contact_lists()
    print(lists)

    contact_list = get_contact_list(contact_list_id=created.id)
    print(contact_list)

    updated = update_contact_list(
        contact_list_id=created.id,
        name=f"{contact_list.name}-updated",
    )
    print(updated)

    deleted = delete_contact_list(contact_list_id=created.id)
    print(deleted)
