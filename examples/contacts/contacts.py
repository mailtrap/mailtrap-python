from typing import Optional
from typing import Union

import mailtrap as mt
from mailtrap.models.common import DeletedObject
from mailtrap.models.contacts import Contact

API_TOKEN = "YOUR_API_TOKEN"
ACCOUNT_ID = "YOUR_ACCOUNT_ID"

client = mt.MailtrapClient(token=API_TOKEN, account_id=ACCOUNT_ID)
contacts_api = client.contacts_api.contacts


def create_contact(
    email: str,
    fields: Optional[dict[str, Union[str, int, float, bool]]] = None,
    list_ids: Optional[list[int]] = None,
) -> Contact:
    params = mt.CreateContactParams(
        email=email,
        fields=fields,
        list_ids=list_ids,
    )
    return contacts_api.create(params)


def update_contact(
    contact_id_or_email: str,
    new_email: Optional[str] = None,
    fields: Optional[dict[str, Union[str, int, float, bool]]] = None,
    list_ids_included: Optional[list[int]] = None,
    list_ids_excluded: Optional[list[int]] = None,
    unsubscribed: Optional[bool] = None,
) -> Contact:
    params = mt.UpdateContactParams(
        email=new_email,
        fields=fields,
        list_ids_included=list_ids_included,
        list_ids_excluded=list_ids_excluded,
        unsubscribed=unsubscribed,
    )
    return contacts_api.update(contact_id_or_email, params)


def get_contact(contact_id_or_email: str) -> Contact:
    return contacts_api.get_by_id(contact_id_or_email)


def delete_contact(contact_id_or_email: str) -> DeletedObject:
    return contacts_api.delete(contact_id_or_email)


if __name__ == "__main__":
    created_contact = create_contact(
        email="testemail@test.com",
        fields={
            "first_name": "Test",
            "last_name": "Test",
        },
    )
    print(created_contact)

    updated_contact = update_contact(
        created_contact.id,
        fields={
            "first_name": "John",
            "last_name": "Doe",
        },
    )
    print(updated_contact)

    contact = get_contact(updated_contact.id)
    print(contact)

    deleted_contact = delete_contact(updated_contact.id)
    print(deleted_contact)
