import os

import mailtrap as mt
from mailtrap.models.common import DeletedObject
from mailtrap.models.organizations import SubAccount

API_KEY = os.environ["MAILTRAP_API_KEY"]
ORGANIZATION_ID = os.environ["MAILTRAP_ORGANIZATION_ID"]

client = mt.MailtrapClient(token=API_KEY, organization_id=ORGANIZATION_ID)
sub_accounts_api = client.organizations_api.sub_accounts


def list_sub_accounts() -> list[SubAccount]:
    return sub_accounts_api.get_list()


def create_sub_account(name: str) -> SubAccount:
    return sub_accounts_api.create(mt.CreateSubAccountParams(name=name))


def delete_sub_account(sub_account_id: int) -> DeletedObject:
    return sub_accounts_api.delete(sub_account_id=sub_account_id)


if __name__ == "__main__":
    sub_accounts = list_sub_accounts()
    print(sub_accounts)

    created = create_sub_account("New Team Account")
    print(created)

    deleted = delete_sub_account(created.id)
    print(deleted)
