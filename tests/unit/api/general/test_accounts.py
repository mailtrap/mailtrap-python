from typing import Any

import pytest
import responses

from mailtrap.api.resources.accounts import AccountsApi
from mailtrap.config import GENERAL_HOST
from mailtrap.exceptions import APIError
from mailtrap.http import HttpClient
from mailtrap.models.accounts import Account
from tests import conftest

BASE_ACCOUNTS_URL = f"https://{GENERAL_HOST}/api/accounts"


@pytest.fixture
def client() -> AccountsApi:
    return AccountsApi(client=HttpClient(GENERAL_HOST))


@pytest.fixture
def sample_account_dict() -> dict[str, Any]:
    return {"id": 26730, "name": "James", "access_levels": [100]}


@pytest.fixture
def sample_accounts_list() -> list[dict[str, Any]]:
    return [
        {"id": 26730, "name": "James", "access_levels": [100]},
        {"id": 26731, "name": "John", "access_levels": [1000]},
    ]


class TestAccountsApi:

    @pytest.mark.parametrize(
        "status_code,response_json,expected_error_message",
        [
            (
                conftest.UNAUTHORIZED_STATUS_CODE,
                conftest.UNAUTHORIZED_RESPONSE,
                conftest.UNAUTHORIZED_ERROR_MESSAGE,
            ),
        ],
    )
    @responses.activate
    def test_get_list_should_raise_api_errors(
        self,
        client: AccountsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.get(
            BASE_ACCOUNTS_URL,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.get_list()

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_list_should_return_accounts_list(
        self, client: AccountsApi, sample_accounts_list: list[dict]
    ) -> None:
        responses.get(
            BASE_ACCOUNTS_URL,
            json=sample_accounts_list,
            status=200,
        )

        accounts = client.get_list()

        assert isinstance(accounts, list)
        assert all(isinstance(account, Account) for account in accounts)
        assert len(accounts) == 2
        assert accounts[0].id == 26730
        assert accounts[0].name == "James"
        assert accounts[0].access_levels == [100]
        assert accounts[1].id == 26731
        assert accounts[1].name == "John"
        assert accounts[1].access_levels == [1000]

    @responses.activate
    def test_get_list_should_return_empty_list(self, client: AccountsApi) -> None:
        responses.get(
            BASE_ACCOUNTS_URL,
            json=[],
            status=200,
        )

        accounts = client.get_list()

        assert isinstance(accounts, list)
        assert len(accounts) == 0
