import os
from typing import Optional

import mailtrap as mt
from mailtrap.models.contacts import ContactImport

API_KEY = os.environ["MAILTRAP_API_KEY"]
ACCOUNT_ID = os.environ["MAILTRAP_ACCOUNT_ID"]

client = mt.MailtrapClient(token=API_KEY, account_id=ACCOUNT_ID)
contact_imports_api = client.contacts_api.contact_imports


def import_contacts(contacts: list[mt.ImportContactParams]) -> ContactImport:
    return contact_imports_api.import_contacts(contacts=contacts)


def find_topic_preference() -> Optional[mt.ContactSubscriptionTopic]:
    # The first subscription topic, on its sending domain or, for a topic that
    # covers every domain, on the first one. The topics list answers 403 when
    # the account has no subscription topics.
    try:
        topics = client.subscription_topics_api.subscription_topics.get_list().data
    except mt.APIError as error:
        if error.status == 403:
            return None
        raise
    if not topics:
        return None
    domain_id = topics[0].domain_id
    if domain_id is None:
        domains = client.domains_api.domains.get_list()
        if not domains:
            return None
        domain_id = domains[0].id
    return mt.ContactSubscriptionTopic(
        subscription_topic_id=topics[0].id, domain_id=domain_id, status="unsubscribed"
    )


def get_contact_import(import_id: int) -> ContactImport:
    return contact_imports_api.get_by_id(import_id)


if __name__ == "__main__":
    preference = find_topic_preference()
    contact_import = import_contacts(
        contacts=[
            mt.ImportContactParams(
                email="testemail@test.com",
                fields={"first_name": "Test", "last_name": "Test"},
                # Left out of the request when None.
                subscription_topics=[preference] if preference else None,
            )
        ]
    )
    print(contact_import)

    contact_import = get_contact_import(contact_import.id)
    print(contact_import)
