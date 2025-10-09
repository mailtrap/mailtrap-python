from typing import Any

import pytest
import responses

from mailtrap.api.resources.contact_exports import ContactExportsApi
from mailtrap.config import GENERAL_HOST
from mailtrap.exceptions import APIError
from mailtrap.http import HttpClient
from mailtrap.models.contacts import ContactExportDetail
from mailtrap.models.contacts import ContactExportFilter
from mailtrap.models.contacts import CreateContactExportParams
from tests import conftest

ACCOUNT_ID = "321"
EXPORT_ID = 1
BASE_CONTACT_EXPORTS_URL = (
    f"https://{GENERAL_HOST}/api/accounts/{ACCOUNT_ID}/contacts/exports"
)


@pytest.fixture
def client() -> ContactExportsApi:
    return ContactExportsApi(account_id=ACCOUNT_ID, client=HttpClient(GENERAL_HOST))


@pytest.fixture
def sample_contact_export_started_dict() -> dict[str, Any]:
    return {
        "id": EXPORT_ID,
        "status": "started",
        "created_at": "2021-01-01T00:00:00Z",
        "updated_at": "2021-01-01T00:00:00Z",
        "url": None,
    }


@pytest.fixture
def sample_contact_export_finished_dict() -> dict[str, Any]:
    return {
        "id": EXPORT_ID,
        "status": "finished",
        "created_at": "2021-01-01T00:00:00Z",
        "updated_at": "2021-01-01T00:00:00Z",
        "url": "https://example.com/export.csv.gz",
    }


@pytest.fixture
def sample_contact_export_filter() -> ContactExportFilter:
    return ContactExportFilter(name="list_id", operator="in", value=[1, 2, 3])


@pytest.fixture
def sample_create_contact_export_params() -> CreateContactExportParams:
    return CreateContactExportParams(
        filters=[ContactExportFilter(name="list_id", operator="in", value=[1, 2, 3])]
    )


class TestContactExportsApi:

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
    def test_create_should_raise_api_errors(
        self,
        client: ContactExportsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
        sample_create_contact_export_params: CreateContactExportParams,
    ) -> None:
        responses.post(
            BASE_CONTACT_EXPORTS_URL,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.create(sample_create_contact_export_params)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_create_should_return_contact_export_detail(
        self,
        client: ContactExportsApi,
        sample_contact_export_started_dict: dict,
        sample_create_contact_export_params: CreateContactExportParams,
    ) -> None:
        responses.post(
            BASE_CONTACT_EXPORTS_URL,
            json=sample_contact_export_started_dict,
            status=201,
        )

        result = client.create(sample_create_contact_export_params)

        assert isinstance(result, ContactExportDetail)
        assert result.id == EXPORT_ID
        assert result.status == "started"
        assert result.url is None
        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert request.url == BASE_CONTACT_EXPORTS_URL

    @responses.activate
    def test_create_should_handle_validation_errors(
        self,
        client: ContactExportsApi,
        sample_create_contact_export_params: CreateContactExportParams,
    ) -> None:
        response_body = {
            "errors": {
                "filters": "invalid",
                "base": [
                    "There is a previous export initiated. "
                    "You will be notified by email once it is completed."
                ],
            }
        }
        responses.post(
            BASE_CONTACT_EXPORTS_URL,
            json=response_body,
            status=422,
        )

        with pytest.raises(APIError) as exc_info:
            client.create(sample_create_contact_export_params)

        assert exc_info.value.status == 422
        assert "filters: invalid" in str(exc_info.value.errors)
        assert (
            "base: There is a previous export initiated. "
            "You will be notified by email once it is completed."
        ) in str(exc_info.value.errors)

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
        client: ContactExportsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        url = f"{BASE_CONTACT_EXPORTS_URL}/{EXPORT_ID}"
        responses.get(
            url,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.get_by_id(EXPORT_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_by_id_should_return_started_export(
        self, client: ContactExportsApi, sample_contact_export_started_dict: dict
    ) -> None:
        url = f"{BASE_CONTACT_EXPORTS_URL}/{EXPORT_ID}"
        responses.get(
            url,
            json=sample_contact_export_started_dict,
            status=200,
        )

        result = client.get_by_id(EXPORT_ID)

        assert isinstance(result, ContactExportDetail)
        assert result.id == EXPORT_ID
        assert result.status == "started"
        assert result.url is None

    @responses.activate
    def test_get_by_id_should_return_finished_export(
        self, client: ContactExportsApi, sample_contact_export_finished_dict: dict
    ) -> None:
        url = f"{BASE_CONTACT_EXPORTS_URL}/{EXPORT_ID}"
        responses.get(
            url,
            json=sample_contact_export_finished_dict,
            status=200,
        )

        result = client.get_by_id(EXPORT_ID)

        assert isinstance(result, ContactExportDetail)
        assert result.id == EXPORT_ID
        assert result.status == "finished"
        assert result.url == "https://example.com/export.csv.gz"

    @responses.activate
    def test_get_by_id_with_different_export_id_should_use_correct_url(
        self, client: ContactExportsApi, sample_contact_export_started_dict: dict
    ) -> None:
        different_export_id = 999
        url = f"{BASE_CONTACT_EXPORTS_URL}/{different_export_id}"
        responses.get(
            url,
            json=sample_contact_export_started_dict,
            status=200,
        )

        client.get_by_id(different_export_id)

        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert request.url == url
