import mailtrap as mt
from mailtrap.models.accounts import Account

API_TOKEN = "YOUR_API_TOKEN"

client = mt.MailtrapClient(token=API_TOKEN)
accounts_api = client.general_api.accounts


def get_accounts() -> list[Account]:
    return accounts_api.get_list()


if __name__ == "__main__":
    print(get_accounts())
