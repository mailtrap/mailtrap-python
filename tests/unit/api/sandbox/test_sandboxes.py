import json
from typing import Any

import pytest
import responses

from mailtrap.api.resources.sandboxes import SandboxesApi
from mailtrap.config import GENERAL_HOST
from mailtrap.exceptions import APIError
from mailtrap.http import HttpClient
from mailtrap.models.sandboxes import CreateSandboxParams
from mailtrap.models.sandboxes import Sandbox
from mailtrap.models.sandboxes import UpdateSandboxParams
from tests import conftest

ACCOUNT_ID = "321"
SANDBOX_ID = 3538
PROJECT_ID = 2293
BASE_INBOXES_URL = f"https://{GENERAL_HOST}/api/accounts/{ACCOUNT_ID}/inboxes"
BASE_PROJECT_INBOXES_URL = (
    f"https://{GENERAL_HOST}/api/accounts/{ACCOUNT_ID}/projects/{PROJECT_ID}/inboxes"
)


@pytest.fixture
def client() -> SandboxesApi:
    return SandboxesApi(account_id=ACCOUNT_ID, client=HttpClient(GENERAL_HOST))


@pytest.fixture
def sample_sandbox_dict() -> dict[str, Any]:
    return {
        "id": SANDBOX_ID,
        "name": "Admin Sandbox",
        "username": "b3a87978452ae1",
        "password": "6be9fcfc613a7c",
        "max_size": 0,
        "status": "active",
        "email_username": "b7eae548c3-54c542",
        "email_username_enabled": False,
        "sent_messages_count": 52,
        "forwarded_messages_count": 0,
        "used": False,
        "forward_from_email_address": "a3538-i4088@forward.mailtrap.info",
        "project_id": PROJECT_ID,
        "domain": "localhost",
        "pop3_domain": "localhost",
        "email_domain": "localhost",
        "api_domain": "localhost",
        "emails_count": 0,
        "emails_unread_count": 0,
        "last_message_sent_at": None,
        "smtp_ports": [25, 465, 587, 2525],
        "pop3_ports": [1100, 9950],
        "max_message_size": 5242880,
        "permissions": {
            "can_read": True,
            "can_update": True,
            "can_destroy": True,
            "can_leave": True,
        },
    }


class TestSandboxesApi:

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
        client: SandboxesApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.get(
            BASE_INBOXES_URL,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.get_list()

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_list_should_return_sandbox_list(
        self, client: SandboxesApi, sample_sandbox_dict: dict
    ) -> None:
        responses.get(
            BASE_INBOXES_URL,
            json=[sample_sandbox_dict],
            status=200,
        )

        sandboxes = client.get_list()

        assert isinstance(sandboxes, list)
        assert all(isinstance(i, Sandbox) for i in sandboxes)
        assert sandboxes[0].id == SANDBOX_ID

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
    def test_get_by_id_should_raise_api_errors(
        self,
        client: SandboxesApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        url = f"{BASE_INBOXES_URL}/{SANDBOX_ID}"
        responses.get(
            url,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.get_by_id(SANDBOX_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_by_id_should_return_single_sandbox(
        self, client: SandboxesApi, sample_sandbox_dict: dict
    ) -> None:
        url = f"{BASE_INBOXES_URL}/{SANDBOX_ID}"
        responses.get(
            url,
            json=sample_sandbox_dict,
            status=200,
        )

        sandbox = client.get_by_id(SANDBOX_ID)

        assert isinstance(sandbox, Sandbox)
        assert sandbox.id == SANDBOX_ID

    @responses.activate
    def test_get_by_id_should_request_sandbox_url_for_id_zero(
        self, client: SandboxesApi, sample_sandbox_dict: dict
    ) -> None:
        responses.get(f"{BASE_INBOXES_URL}/0", json=sample_sandbox_dict, status=200)

        sandbox = client.get_by_id(0)

        assert isinstance(sandbox, Sandbox)

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
    def test_create_should_raise_api_errors(
        self,
        client: SandboxesApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.post(
            BASE_PROJECT_INBOXES_URL,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.create(
                project_id=PROJECT_ID,
                sandbox_params=CreateSandboxParams(name="New Sandbox"),
            )

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_create_should_return_new_sandbox(
        self, client: SandboxesApi, sample_sandbox_dict: dict
    ) -> None:
        responses.post(
            BASE_PROJECT_INBOXES_URL,
            json=sample_sandbox_dict,
            status=201,
        )

        sandbox = client.create(
            project_id=PROJECT_ID, sandbox_params=CreateSandboxParams(name="New Sandbox")
        )

        assert isinstance(sandbox, Sandbox)
        assert sandbox.name == "Admin Sandbox"
        assert responses.calls[0].request.body is not None
        assert json.loads(responses.calls[0].request.body) == {
            "inbox": {"name": "New Sandbox"}
        }

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
    def test_update_should_raise_api_errors(
        self,
        client: SandboxesApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        url = f"{BASE_INBOXES_URL}/{SANDBOX_ID}"
        responses.patch(
            url,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            _ = client.update(
                SANDBOX_ID,
                sandbox_params=UpdateSandboxParams(name="Updated Sandbox Name"),
            )

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_update_should_return_updated_sandbox(
        self, client: SandboxesApi, sample_sandbox_dict: dict
    ) -> None:
        url = f"{BASE_INBOXES_URL}/{SANDBOX_ID}"
        updated_name = "Updated Sandbox"
        updated_sandbox_dict = sample_sandbox_dict.copy()
        updated_sandbox_dict["name"] = updated_name

        responses.patch(
            url,
            json=updated_sandbox_dict,
            status=200,
        )

        sandbox = client.update(
            SANDBOX_ID, sandbox_params=UpdateSandboxParams(name=updated_name)
        )

        assert isinstance(sandbox, Sandbox)
        assert sandbox.name == updated_name
        assert responses.calls[0].request.body is not None
        assert json.loads(responses.calls[0].request.body) == {
            "inbox": {"name": updated_name}
        }

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
        client: SandboxesApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        url = f"{BASE_INBOXES_URL}/{SANDBOX_ID}"
        responses.delete(
            url,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.delete(SANDBOX_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_delete_should_return_deleted_sandbox(
        self, client: SandboxesApi, sample_sandbox_dict: dict
    ) -> None:
        url = f"{BASE_INBOXES_URL}/{SANDBOX_ID}"
        responses.delete(
            url,
            json=sample_sandbox_dict,
            status=200,
        )

        result = client.delete(SANDBOX_ID)

        assert isinstance(result, Sandbox)
        assert result.id == SANDBOX_ID

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
    def test_clean_should_raise_api_errors(
        self,
        client: SandboxesApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        url = f"{BASE_INBOXES_URL}/{SANDBOX_ID}/clean"
        responses.patch(
            url,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.clean(SANDBOX_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_clean_should_return_cleaned_sandbox(
        self, client: SandboxesApi, sample_sandbox_dict: dict
    ) -> None:
        url = f"{BASE_INBOXES_URL}/{SANDBOX_ID}/clean"
        responses.patch(
            url,
            json=sample_sandbox_dict,
            status=200,
        )

        result = client.clean(SANDBOX_ID)

        assert isinstance(result, Sandbox)
        assert result.id == SANDBOX_ID

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
    def test_mark_as_read_should_raise_api_errors(
        self,
        client: SandboxesApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        url = f"{BASE_INBOXES_URL}/{SANDBOX_ID}/all_read"
        responses.patch(
            url,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.mark_as_read(SANDBOX_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_mark_as_read_should_return_sandbox(
        self, client: SandboxesApi, sample_sandbox_dict: dict
    ) -> None:
        url = f"{BASE_INBOXES_URL}/{SANDBOX_ID}/all_read"
        responses.patch(
            url,
            json=sample_sandbox_dict,
            status=200,
        )

        result = client.mark_as_read(SANDBOX_ID)

        assert isinstance(result, Sandbox)
        assert result.id == SANDBOX_ID

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
    def test_reset_credentials_should_raise_api_errors(
        self,
        client: SandboxesApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        url = f"{BASE_INBOXES_URL}/{SANDBOX_ID}/reset_credentials"
        responses.patch(
            url,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.reset_credentials(SANDBOX_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_reset_credentials_should_return_sandbox(
        self, client: SandboxesApi, sample_sandbox_dict: dict
    ) -> None:
        url = f"{BASE_INBOXES_URL}/{SANDBOX_ID}/reset_credentials"
        responses.patch(
            url,
            json=sample_sandbox_dict,
            status=200,
        )

        result = client.reset_credentials(SANDBOX_ID)

        assert isinstance(result, Sandbox)
        assert result.id == SANDBOX_ID

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
    def test_enable_email_address_should_raise_api_errors(
        self,
        client: SandboxesApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        url = f"{BASE_INBOXES_URL}/{SANDBOX_ID}/toggle_email_username"
        responses.patch(
            url,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.enable_email_address(SANDBOX_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_enable_email_address_should_return_sandbox(
        self, client: SandboxesApi, sample_sandbox_dict: dict
    ) -> None:
        url = f"{BASE_INBOXES_URL}/{SANDBOX_ID}/toggle_email_username"
        responses.patch(
            url,
            json=sample_sandbox_dict,
            status=200,
        )

        result = client.enable_email_address(SANDBOX_ID)

        assert isinstance(result, Sandbox)
        assert result.id == SANDBOX_ID

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
    def test_reset_email_username_should_raise_api_errors(
        self,
        client: SandboxesApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        url = f"{BASE_INBOXES_URL}/{SANDBOX_ID}/reset_email_username"
        responses.patch(
            url,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.reset_email_username(SANDBOX_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_reset_email_username_should_return_sandbox(
        self, client: SandboxesApi, sample_sandbox_dict: dict
    ) -> None:
        url = f"{BASE_INBOXES_URL}/{SANDBOX_ID}/reset_email_username"
        responses.patch(
            url,
            json=sample_sandbox_dict,
            status=200,
        )

        result = client.reset_email_username(SANDBOX_ID)

        assert isinstance(result, Sandbox)
        assert result.id == SANDBOX_ID
