from typing import Any

import pytest
import responses

from mailtrap.api.resources.api_tokens import ApiTokensApi
from mailtrap.config import GENERAL_HOST
from mailtrap.exceptions import APIError
from mailtrap.http import HttpClient
from mailtrap.models.api_tokens import ApiToken
from tests import conftest

ACCOUNT_ID = 26730
API_TOKEN_ID = 12345
BASE_API_TOKENS_URL = f"https://{GENERAL_HOST}/api/accounts/{ACCOUNT_ID}/api_tokens"


@pytest.fixture
def client() -> ApiTokensApi:
    return ApiTokensApi(client=HttpClient(GENERAL_HOST))


@pytest.fixture
def sample_api_token_dict() -> dict[str, Any]:
    return {
        "id": API_TOKEN_ID,
        "name": "My API Token",
        "last_4_digits": "x7k9",
        "created_by": "user@example.com",
        "expires_at": None,
        "resources": [
            {"resource_type": "account", "resource_id": 3229, "access_level": 100}
        ],
    }


class TestApiTokensApi:

    @pytest.mark.parametrize(
        "status_code,response_json,expected_error_message",
        [
            (
                conftest.UNAUTHORIZED_STATUS_CODE,
                conftest.UNAUTHORIZED_RESPONSE,
                conftest.UNAUTHORIZED_ERROR_MESSAGE,
            ),
            (
                conftest.FORBIDDEN_STATUS_CODE,
                conftest.FORBIDDEN_RESPONSE,
                conftest.FORBIDDEN_ERROR_MESSAGE,
            ),
        ],
    )
    @responses.activate
    def test_get_list_should_raise_api_errors(
        self,
        client: ApiTokensApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.get(
            BASE_API_TOKENS_URL,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.get_list(ACCOUNT_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_list_should_return_api_tokens_list(
        self, client: ApiTokensApi, sample_api_token_dict: dict
    ) -> None:
        responses.get(
            BASE_API_TOKENS_URL,
            json=[sample_api_token_dict],
            status=200,
        )

        api_tokens = client.get_list(ACCOUNT_ID)

        assert isinstance(api_tokens, list)
        assert all(isinstance(token, ApiToken) for token in api_tokens)
        assert len(api_tokens) == 1
        assert api_tokens[0].id == API_TOKEN_ID
        assert api_tokens[0].name == "My API Token"
        assert api_tokens[0].last_4_digits == "x7k9"
        assert api_tokens[0].created_by == "user@example.com"
        assert api_tokens[0].expires_at is None
        assert len(api_tokens[0].resources) == 1
        assert api_tokens[0].resources[0].resource_type == "account"
        assert api_tokens[0].resources[0].resource_id == 3229
        assert api_tokens[0].resources[0].access_level == 100

    @responses.activate
    def test_get_list_should_return_empty_list(self, client: ApiTokensApi) -> None:
        responses.get(
            BASE_API_TOKENS_URL,
            json=[],
            status=200,
        )

        api_tokens = client.get_list(ACCOUNT_ID)

        assert isinstance(api_tokens, list)
        assert len(api_tokens) == 0
