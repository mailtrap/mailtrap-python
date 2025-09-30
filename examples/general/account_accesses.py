import mailtrap as mt
from mailtrap.models.accounts import AccountAccess
from mailtrap.models.common import DeletedObject

API_TOKEN = "YOUR_API_TOKEN"
ACCOUNT_ID = "YOUR_ACCOUNT_ID"

client = mt.MailtrapClient(token=API_TOKEN)
account_accesses_api = client.general_api.account_accesses


def get_account_accesses(account_id: int) -> list[AccountAccess]:
    return account_accesses_api.get_list(account_id=account_id)


def delete_account_access(account_id: int, account_access_id: int) -> DeletedObject:
    return account_accesses_api.delete(
        account_id=account_id, account_access_id=account_access_id
    )


if __name__ == "__main__":
    print(get_account_accesses(ACCOUNT_ID))
