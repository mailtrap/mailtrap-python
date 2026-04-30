from mailtrap.http import HttpClient
from mailtrap.models.api_tokens import ApiToken


class ApiTokensApi:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def get_list(self, account_id: int) -> list[ApiToken]:
        """
        Returns all API tokens visible to the current API token.
        """
        response = self._client.get(self._api_path(account_id))
        return [ApiToken(**api_token) for api_token in response]

    @staticmethod
    def _api_path(account_id: int) -> str:
        return f"/api/accounts/{account_id}/api_tokens"
