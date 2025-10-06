from mailtrap.http import HttpClient
from mailtrap.models.accounts import Account


class AccountsApi:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def get_list(self) -> list[Account]:
        """Get a list of your Mailtrap accounts."""
        response = self._client.get("/api/accounts")
        return [Account(**account) for account in response]
