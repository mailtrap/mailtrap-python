import mailtrap as mt
from mailtrap.models.api_tokens import ApiToken

API_TOKEN = "YOUR_API_TOKEN"
ACCOUNT_ID = "YOUR_ACCOUNT_ID"

client = mt.MailtrapClient(token=API_TOKEN)
api_tokens_api = client.general_api.api_tokens


def get_api_tokens(account_id: int) -> list[ApiToken]:
    return api_tokens_api.get_list(account_id=account_id)


if __name__ == "__main__":
    tokens = get_api_tokens(ACCOUNT_ID)
    print(tokens)
