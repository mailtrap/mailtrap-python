from typing import Optional

from mailtrap.http import HttpClient
from mailtrap.models.api_tokens import ApiToken
from mailtrap.models.api_tokens import ApiTokenWithToken
from mailtrap.models.api_tokens import CreateApiTokenParams
from mailtrap.models.common import DeletedObject


class ApiTokensApi:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def get_list(self, account_id: int) -> list[ApiToken]:
        """
        Returns all API tokens visible to the current API token.
        """
        response = self._client.get(self._api_path(account_id))
        return [ApiToken(**api_token) for api_token in response]

    def get_by_id(self, account_id: int, api_token_id: int) -> ApiToken:
        """
        Get a single API token by id.
        """
        response = self._client.get(self._api_path(account_id, api_token_id))
        return ApiToken(**response)

    def create(
        self, account_id: int, token_params: CreateApiTokenParams
    ) -> ApiTokenWithToken:
        """
        Create a new API token. The full token value is only returned once
        in the response — store it securely.
        """
        response = self._client.post(
            self._api_path(account_id), json=token_params.api_data
        )
        return ApiTokenWithToken(**response)

    def delete(self, account_id: int, api_token_id: int) -> DeletedObject:
        """
        Permanently delete an API token.
        """
        self._client.delete(self._api_path(account_id, api_token_id))
        return DeletedObject(id=api_token_id)

    def reset(self, account_id: int, api_token_id: int) -> ApiTokenWithToken:
        """
        Expire the requested token and create a new token with the same
        permissions. The full new token value is returned once — store it
        securely. Only tokens that have not already been reset can be reset.
        """
        response = self._client.post(f"{self._api_path(account_id, api_token_id)}/reset")
        return ApiTokenWithToken(**response)

    @staticmethod
    def _api_path(account_id: int, api_token_id: Optional[int] = None) -> str:
        path = f"/api/accounts/{account_id}/api_tokens"
        if api_token_id is not None:
            return f"{path}/{api_token_id}"
        return path
