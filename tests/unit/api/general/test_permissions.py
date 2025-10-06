from typing import Any

import pytest
import responses

from mailtrap.api.resources.permissions import PermissionsApi
from mailtrap.config import GENERAL_HOST
from mailtrap.exceptions import APIError
from mailtrap.http import HttpClient
from mailtrap.models.permissions import PermissionResource
from mailtrap.models.permissions import PermissionResourceParams
from mailtrap.models.permissions import UpdatePermissionsResponse
from tests import conftest

ACCOUNT_ID = 26730
ACCOUNT_ACCESS_ID = 5142
BASE_PERMISSIONS_URL = (
    f"https://{GENERAL_HOST}/api/accounts/{ACCOUNT_ID}/permissions/resources"
)
BASE_BULK_PERMISSIONS_URL = (
    f"https://{GENERAL_HOST}/api/accounts"
    f"/{ACCOUNT_ID}/account_accesses"
    f"/{ACCOUNT_ACCESS_ID}/permissions/bulk"
)


@pytest.fixture
def client() -> PermissionsApi:
    return PermissionsApi(client=HttpClient(GENERAL_HOST))


@pytest.fixture
def sample_permission_resource_dict() -> dict[str, Any]:
    return {
        "id": 1,
        "name": "Test Project",
        "type": "project",
        "access_level": 100,
        "resources": [
            {
                "id": 2,
                "name": "Test Inbox",
                "type": "inbox",
                "access_level": 100,
                "resources": [],
            }
        ],
    }


@pytest.fixture
def sample_permission_params() -> list[PermissionResourceParams]:
    return [
        PermissionResourceParams(
            resource_id="3281", resource_type="account", access_level="viewer"
        ),
        PermissionResourceParams(
            resource_id="3809", resource_type="inbox", _destroy=True
        ),
    ]


@pytest.fixture
def sample_update_permissions_response_dict() -> dict[str, Any]:
    return {"message": "Permissions have been updated!"}


class TestPermissionsApi:

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
    def test_get_resources_should_raise_api_errors(
        self,
        client: PermissionsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.get(
            BASE_PERMISSIONS_URL,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.get_resources(ACCOUNT_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_resources_should_return_permission_resources_list(
        self, client: PermissionsApi, sample_permission_resource_dict: dict
    ) -> None:
        responses.get(
            BASE_PERMISSIONS_URL,
            json=[sample_permission_resource_dict],
            status=200,
        )

        resources = client.get_resources(ACCOUNT_ID)

        assert isinstance(resources, list)
        assert all(isinstance(resource, PermissionResource) for resource in resources)
        assert len(resources) == 1
        assert resources[0].id == 1
        assert resources[0].name == "Test Project"
        assert resources[0].type == "project"
        assert resources[0].access_level == 100
        assert len(resources[0].resources) == 1
        assert resources[0].resources[0].name == "Test Inbox"

    @responses.activate
    def test_get_resources_should_return_empty_list(self, client: PermissionsApi) -> None:
        responses.get(
            BASE_PERMISSIONS_URL,
            json=[],
            status=200,
        )

        resources = client.get_resources(ACCOUNT_ID)

        assert isinstance(resources, list)
        assert len(resources) == 0

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
    def test_bulk_permissions_update_should_raise_api_errors(
        self,
        client: PermissionsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.put(
            BASE_BULK_PERMISSIONS_URL,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.bulk_permissions_update(ACCOUNT_ID, ACCOUNT_ACCESS_ID, [])

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_bulk_permissions_update_should_return_update_response(
        self,
        client: PermissionsApi,
        sample_permission_params: list[PermissionResourceParams],
        sample_update_permissions_response_dict: dict,
    ) -> None:
        responses.put(
            BASE_BULK_PERMISSIONS_URL,
            json=sample_update_permissions_response_dict,
            status=200,
        )

        result = client.bulk_permissions_update(
            ACCOUNT_ID, ACCOUNT_ACCESS_ID, sample_permission_params
        )

        assert isinstance(result, UpdatePermissionsResponse)
        assert result.message == "Permissions have been updated!"
