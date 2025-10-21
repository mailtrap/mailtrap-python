import mailtrap as mt
from mailtrap.models.contacts import ContactEvent

API_TOKEN = "YOUR_API_TOKEN"
ACCOUNT_ID = "YOUR_ACCOUNT_ID"

client = mt.MailtrapClient(token=API_TOKEN, account_id=ACCOUNT_ID)
contact_events_api = client.contacts_api.contact_events


def create_contact_event(
    contact_identifier: str,
    contact_event_params: mt.ContactEventParams,
) -> ContactEvent:
    return contact_events_api.create(
        contact_identifier=contact_identifier,
        contact_event_params=contact_event_params,
    )


if __name__ == "__main__":
    contact_event = create_contact_event(
        contact_identifier="01988623-832f-79df-8aae-a480f8ff7249",
        contact_event_params=mt.ContactEventParams(
            name="UserLogin",
            params={
                "user_id": 101,
                "user_name": "John Smith",
                "is_active": True,
                "last_seen": None,
            },
        ),
    )
    print(contact_event)
