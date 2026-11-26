import os

import mailtrap as mt
from mailtrap.models.suppressions import Suppression

API_KEY = os.environ["MAILTRAP_API_KEY"]
ACCOUNT_ID = os.environ["MAILTRAP_ACCOUNT_ID"]

client = mt.MailtrapClient(token=API_KEY, account_id=ACCOUNT_ID)
suppressions_api = client.suppressions_api.suppressions


def list_suppressions(email: str | None = None) -> list[Suppression]:
    return suppressions_api.get_list(email)


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
