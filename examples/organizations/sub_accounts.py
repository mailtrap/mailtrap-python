import mailtrap as mt
from mailtrap.models.organizations import SubAccount

API_TOKEN = "YOUR_API_TOKEN"
ORGANIZATION_ID = "YOUR_ORGANIZATION_ID"

client = mt.MailtrapClient(token=API_TOKEN, organization_id=ORGANIZATION_ID)
sub_accounts_api = client.organizations_api.sub_accounts


def list_sub_accounts() -> list[SubAccount]:
    return sub_accounts_api.get_list()


def create_sub_account(name: str) -> SubAccount:
    return sub_accounts_api.create(mt.CreateSubAccountParams(name=name))


if __name__ == "__main__":
    sub_accounts = list_sub_accounts()
    print(sub_accounts)

    created = create_sub_account("New Team Account")
    print(created)
