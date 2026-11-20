import os
from typing import Optional
from typing import Union

import mailtrap as mt
from mailtrap.models.common import DeletedObject
from mailtrap.models.contacts import Contact

API_KEY = os.environ["MAILTRAP_API_KEY"]
ACCOUNT_ID = os.environ["MAILTRAP_ACCOUNT_ID"]

client = mt.MailtrapClient(token=API_KEY, account_id=ACCOUNT_ID)
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


def set_subscription_topic_status(
    contact_id_or_email: str, preference: mt.ContactSubscriptionTopic
) -> Contact:
    # Only the given topic on the given sending domain changes; the contact's
    # other topic preferences keep their status.
    params = mt.UpdateContactParams(subscription_topics=[preference])
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

    # The contact's status for every subscription topic on every sending
    # domain; None when the account has no subscription topics.
    if contact.subscription_topics:
        preference = contact.subscription_topics[0]
        unsubscribed_contact = set_subscription_topic_status(
            contact.id,
            mt.ContactSubscriptionTopic(
                subscription_topic_id=preference.subscription_topic_id,
                domain_id=preference.domain_id,
                status="unsubscribed",
            ),
        )
        print(unsubscribed_contact.subscription_topics)

    deleted_contact = delete_contact(updated_contact.id)
    print(deleted_contact)
