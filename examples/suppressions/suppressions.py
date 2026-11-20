import os
from typing import Optional

import mailtrap as mt
from mailtrap.models.suppressions import Suppression

API_KEY = os.environ["MAILTRAP_API_KEY"]
ACCOUNT_ID = os.environ["MAILTRAP_ACCOUNT_ID"]

client = mt.MailtrapClient(token=API_KEY, account_id=ACCOUNT_ID)
suppressions_api = client.suppressions_api.suppressions


def list_suppressions(
    email: Optional[str] = None, include_topic_unsubscriptions: bool = False
) -> list[Suppression]:
    # With `include_topic_unsubscriptions`, the list also has unsubscribes from
    # single subscription topics, of type "topic unsubscription".
    return suppressions_api.get_list(
        email, include_topic_unsubscriptions=include_topic_unsubscriptions
    )


def create_suppression() -> Suppression:
    params = mt.CreateSuppressionParams(
        email="recipient@example.com",
        domain_id=12345,
        sending_stream="transactional",
    )
    return suppressions_api.create(params)


def delete_suppression(suppression_id: str) -> Suppression:
    return suppressions_api.delete(suppression_id)


if __name__ == "__main__":
    created = create_suppression()
    print(created)

    suppressions = list_suppressions()
    print(suppressions)
    if suppressions:
        deleted_suppression = delete_suppression(suppressions[0].id)
        print(deleted_suppression)

    # A topic unsubscription can't be deleted, so only print them.
    for suppression in list_suppressions(include_topic_unsubscriptions=True):
        if suppression.type == "topic unsubscription":
            print(
                f"{suppression.email} left topic {suppression.subscription_topic_id}"
                f" on {suppression.domain_name}"
            )
