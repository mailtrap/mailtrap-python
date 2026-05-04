from typing import Any

import pytest
import responses

from mailtrap.api.resources.sub_accounts import SubAccountsApi
from mailtrap.config import GENERAL_HOST
from mailtrap.exceptions import APIError
from mailtrap.http import HttpClient
from mailtrap.models.organizations import CreateSubAccountParams
from mailtrap.models.organizations import SubAccount
from tests import conftest

ORGANIZATION_ID = "1001"
SUB_ACCOUNT_ID = 12345
BASE_SUB_ACCOUNTS_URL = (
    f"https://{GENERAL_HOST}/api/organizations/{ORGANIZATION_ID}/sub_accounts"
)


@pytest.fixture
def client() -> SubAccountsApi:
    return SubAccountsApi(
        client=HttpClient(GENERAL_HOST), organization_id=ORGANIZATION_ID
    )


@pytest.fixture
def sample_sub_account_dict() -> dict[str, Any]:
    return {"id": SUB_ACCOUNT_ID, "name": "Development Team Account"}


class TestSubAccountsApi:

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
        client: SubAccountsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.get(
            BASE_SUB_ACCOUNTS_URL,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.get_list()

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_list_should_return_sub_accounts_list(
        self, client: SubAccountsApi, sample_sub_account_dict: dict
    ) -> None:
        responses.get(
            BASE_SUB_ACCOUNTS_URL,
            json=[
                sample_sub_account_dict,
                {"id": 12346, "name": "QA Team Account"},
            ],
            status=200,
        )

        sub_accounts = client.get_list()

        assert isinstance(sub_accounts, list)
        assert all(isinstance(s, SubAccount) for s in sub_accounts)
        assert len(sub_accounts) == 2
        assert sub_accounts[0].id == SUB_ACCOUNT_ID
        assert sub_accounts[0].name == "Development Team Account"

    @responses.activate
    def test_get_list_should_return_empty_list(self, client: SubAccountsApi) -> None:
        responses.get(BASE_SUB_ACCOUNTS_URL, json=[], status=200)

        sub_accounts = client.get_list()

        assert isinstance(sub_accounts, list)
        assert len(sub_accounts) == 0

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
            (
                conftest.VALIDATION_ERRORS_STATUS_CODE,
                {"errors": "Name is invalid"},
                "Name is invalid",
            ),
        ],
    )
    @responses.activate
    def test_create_should_raise_api_errors(
        self,
        client: SubAccountsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.post(BASE_SUB_ACCOUNTS_URL, status=status_code, json=response_json)

        with pytest.raises(APIError) as exc_info:
            client.create(CreateSubAccountParams(name="New Team Account"))

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_create_should_return_sub_account_and_wrap_body_under_account_key(
        self, client: SubAccountsApi, sample_sub_account_dict: dict
    ) -> None:
        responses.post(
            BASE_SUB_ACCOUNTS_URL,
            json={"id": 12347, "name": "New Team Account"},
            status=200,
        )

        sub_account = client.create(CreateSubAccountParams(name="New Team Account"))

        assert isinstance(sub_account, SubAccount)
        assert sub_account.id == 12347
        assert sub_account.name == "New Team Account"

        assert len(responses.calls) == 1
        assert (
            responses.calls[0].request.body
            == b'{"account": {"name": "New Team Account"}}'
        )
