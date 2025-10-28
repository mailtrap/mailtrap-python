from typing import Optional

import mailtrap as mt
from mailtrap.models.suppressions import Suppression

API_TOKEN = "YOUR_API_TOKEN"
ACCOUNT_ID = "YOUR_ACCOUNT_ID"

client = mt.MailtrapClient(token=API_TOKEN, account_id=ACCOUNT_ID)
suppressions_api = client.suppressions_api.suppressions


def list_suppressions(email: Optional[str] = None) -> list[Suppression]:
    return suppressions_api.get_list(email)


def delete_suppression(suppression_id: str) -> Suppression:
    return suppressions_api.delete(suppression_id)


if __name__ == "__main__":
    suppressions = list_suppressions()
    print(suppressions)
    if suppressions:
        deleted_suppression = delete_suppression(suppressions[0].id)
        print(deleted_suppression)
