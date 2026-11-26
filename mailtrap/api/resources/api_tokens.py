from mailtrap.http import HttpClient
from mailtrap.models.api_tokens import ApiToken
from mailtrap.models.api_tokens import ApiTokenWithToken
from mailtrap.models.api_tokens import CreateApiTokenParams
from mailtrap.models.api_tokens import ResetApiTokenParams
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

        expires_at is an optional token expiration as an ISO 8601 date-time.
        Omit it for the server default of 1 year. Pass an explicit None for
        a token that never expires. Past or more-than-5-years-ahead values
        are rejected with a 422 error.
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

    def reset(
        self,
        account_id: int,
        api_token_id: int,
        token_params: ResetApiTokenParams | None = None,
    ) -> ApiTokenWithToken:
        """
        Expire the requested token and create a new token with the same
        permissions. The full new token value is returned once — store it
        securely. Tokens that have already expired cannot be reset.

        expires_at is an optional expiration of the new token as an ISO 8601
        date-time. Omit token_params or expires_at for the server default of
        1 year. Pass an explicit None for a token that never expires. Past or
        more-than-5-years-ahead values are rejected with a 422 error.
        """
        response = self._client.post(
            f"{self._api_path(account_id, api_token_id)}/reset",
            json=token_params.api_data if token_params is not None else None,
        )
        return ApiTokenWithToken(**response)

    @staticmethod
    def _api_path(account_id: int, api_token_id: int | None = None) -> str:
        path = f"/api/accounts/{account_id}/api_tokens"
        if api_token_id is not None:
            return f"{path}/{api_token_id}"
        return path
