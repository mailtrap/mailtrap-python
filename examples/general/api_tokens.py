import mailtrap as mt
from mailtrap.models.api_tokens import ApiToken
from mailtrap.models.api_tokens import ApiTokenWithToken
from mailtrap.models.common import DeletedObject

API_TOKEN = "YOUR_API_TOKEN"
ACCOUNT_ID = "YOUR_ACCOUNT_ID"

client = mt.MailtrapClient(token=API_TOKEN)
api_tokens_api = client.general_api.api_tokens


def list_api_tokens(account_id: int) -> list[ApiToken]:
    return api_tokens_api.get_list(account_id=account_id)


def get_api_token(account_id: int, api_token_id: int) -> ApiToken:
    return api_tokens_api.get_by_id(
        account_id=account_id, api_token_id=api_token_id
    )


def create_api_token(account_id: int) -> ApiTokenWithToken:
    # The full token value is only returned once on the response — store it securely.
    return api_tokens_api.create(
        account_id=account_id,
        token_params=mt.CreateApiTokenParams(
            name="My API Token",
            resources=[
                mt.ApiTokenResource(
                    resource_type="account",
                    resource_id=account_id,
                    access_level=100,
                )
            ],
        ),
    )


def reset_api_token(account_id: int, api_token_id: int) -> ApiTokenWithToken:
    # The reset response includes the new full token value once — store it securely.
    return api_tokens_api.reset(
        account_id=account_id, api_token_id=api_token_id
    )


def delete_api_token(account_id: int, api_token_id: int) -> DeletedObject:
    return api_tokens_api.delete(
        account_id=account_id, api_token_id=api_token_id
    )


if __name__ == "__main__":
    tokens = list_api_tokens(ACCOUNT_ID)
    print(tokens)

    created = create_api_token(ACCOUNT_ID)
    print(created)

    fetched = get_api_token(ACCOUNT_ID, created.id)
    print(fetched)

    reset = reset_api_token(ACCOUNT_ID, created.id)
    print(reset)

    deleted = delete_api_token(ACCOUNT_ID, reset.id)
    print(deleted)
