from typing import Any

import pytest
import responses

from mailtrap.api.resources.account_accesses import AccountAccessesApi
from mailtrap.config import GENERAL_HOST
from mailtrap.exceptions import APIError
from mailtrap.http import HttpClient
from mailtrap.models.accounts import AccountAccess
from mailtrap.models.accounts import AccountAccessFilterParams
from mailtrap.models.common import DeletedObject
from tests import conftest

ACCOUNT_ID = 26730
ACCOUNT_ACCESS_ID = 4788
BASE_ACCOUNT_ACCESSES_URL = (
    f"https://{GENERAL_HOST}/api/accounts/{ACCOUNT_ID}/account_accesses"
)


@pytest.fixture
def client() -> AccountAccessesApi:
    return AccountAccessesApi(client=HttpClient(GENERAL_HOST))


@pytest.fixture
def sample_account_access_dict() -> dict[str, Any]:
    return {
        "id": ACCOUNT_ACCESS_ID,
        "specifier_type": "User",
        "specifier": {
            "id": 1234,
            "email": "user@example.com",
            "name": "John Doe",
            "two_factor_authentication_enabled": True,
        },
        "resources": [
            {"resource_id": 1, "resource_type": "project", "access_level": 100}
        ],
        "permissions": {
            "can_read": True,
            "can_update": True,
            "can_destroy": False,
            "can_leave": False,
        },
    }


@pytest.fixture
def sample_filter_params() -> AccountAccessFilterParams:
    return AccountAccessFilterParams(
        project_ids=["3938"], inbox_ids=["3757"], domain_ids=["3883"]
    )


class TestAccountAccessesApi:

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
        client: AccountAccessesApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.get(
            BASE_ACCOUNT_ACCESSES_URL,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.get_list(ACCOUNT_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_list_should_return_account_accesses_list(
        self, client: AccountAccessesApi, sample_account_access_dict: dict
    ) -> None:
        responses.get(
            BASE_ACCOUNT_ACCESSES_URL,
            json=[sample_account_access_dict],
            status=200,
        )

        account_accesses = client.get_list(ACCOUNT_ID)

        assert isinstance(account_accesses, list)
        assert all(isinstance(access, AccountAccess) for access in account_accesses)
        assert len(account_accesses) == 1
        assert account_accesses[0].id == ACCOUNT_ACCESS_ID
        assert account_accesses[0].specifier_type == "User"
        assert account_accesses[0].specifier.email == "user@example.com"

    @responses.activate
    def test_get_list_with_filter_params_should_include_query_params(
        self,
        client: AccountAccessesApi,
        sample_account_access_dict: dict,
        sample_filter_params: AccountAccessFilterParams,
    ) -> None:
        responses.get(
            BASE_ACCOUNT_ACCESSES_URL,
            json=[sample_account_access_dict],
            status=200,
        )

        client.get_list(ACCOUNT_ID, sample_filter_params)

        # Verify the request was made with correct parameters
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert "project_ids=3938" in request.url
        assert "inbox_ids=3757" in request.url
        assert "domain_ids=3883" in request.url

    @responses.activate
    def test_get_list_should_return_empty_list(self, client: AccountAccessesApi) -> None:
        responses.get(
            BASE_ACCOUNT_ACCESSES_URL,
            json=[],
            status=200,
        )

        account_accesses = client.get_list(ACCOUNT_ID)

        assert isinstance(account_accesses, list)
        assert len(account_accesses) == 0

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
                conftest.NOT_FOUND_STATUS_CODE,
                conftest.NOT_FOUND_RESPONSE,
                conftest.NOT_FOUND_ERROR_MESSAGE,
            ),
        ],
    )
    @responses.activate
    def test_delete_should_raise_api_errors(
        self,
        client: AccountAccessesApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        url = f"{BASE_ACCOUNT_ACCESSES_URL}/{ACCOUNT_ACCESS_ID}"
        responses.delete(
            url,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.delete(ACCOUNT_ID, ACCOUNT_ACCESS_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_delete_should_return_deleted_object(
        self, client: AccountAccessesApi
    ) -> None:
        url = f"{BASE_ACCOUNT_ACCESSES_URL}/{ACCOUNT_ACCESS_ID}"
        responses.delete(
            url,
            status=200,
            json={"id": ACCOUNT_ACCESS_ID},
        )

        result = client.delete(ACCOUNT_ID, ACCOUNT_ACCESS_ID)

        assert isinstance(result, DeletedObject)
        assert result.id == ACCOUNT_ACCESS_ID
