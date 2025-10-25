from typing import Any

import pytest
import responses

from mailtrap.api.resources.contact_imports import ContactImportsApi
from mailtrap.config import GENERAL_HOST
from mailtrap.exceptions import APIError
from mailtrap.http import HttpClient
from mailtrap.models.contacts import ContactImport
from mailtrap.models.contacts import ImportContactParams
from tests import conftest

ACCOUNT_ID = "321"
IMPORT_ID = 1234
BASE_CONTACT_IMPORTS_URL = (
    f"https://{GENERAL_HOST}/api/accounts/{ACCOUNT_ID}/contacts/imports"
)


@pytest.fixture
def contact_imports_api() -> ContactImportsApi:
    return ContactImportsApi(account_id=ACCOUNT_ID, client=HttpClient(GENERAL_HOST))


@pytest.fixture
def sample_contact_import_dict() -> dict[str, Any]:
    return {
        "id": IMPORT_ID,
        "status": "started",
    }


@pytest.fixture
def sample_finished_contact_import_dict() -> dict[str, Any]:
    return {
        "id": IMPORT_ID,
        "status": "finished",
        "created_contacts_count": 1,
        "updated_contacts_count": 3,
        "contacts_over_limit_count": 3,
    }


@pytest.fixture
def import_contacts_params() -> list[ImportContactParams]:
    return [
        ImportContactParams(
            email="john.smith@example.com",
            fields={"first_name": "John", "last_name": "Smith"},
            list_ids_included=[1],
            list_ids_excluded=[2],
        ),
        ImportContactParams(
            email="john.doe@example.com",
            fields={"first_name": "John", "last_name": "Doe"},
            list_ids_included=[3],
            list_ids_excluded=[4],
        ),
    ]


class TestContactImportsApi:

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
                {
                    "errors": [
                        {
                            "email": "test@example.com",
                            "errors": {
                                "base": [
                                    "contacts limit reached",
                                    "cannot import more than 50000 contacts at once",
                                ],
                            },
                        }
                    ]
                },
                "contacts limit reached",
            ),
        ],
    )
    @responses.activate
    def test_import_contacts_should_raise_api_errors(
        self,
        contact_imports_api: ContactImportsApi,
        import_contacts_params: list[ImportContactParams],
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.post(
            BASE_CONTACT_IMPORTS_URL,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            _ = contact_imports_api.import_contacts(import_contacts_params)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_import_contacts_should_return_started_import(
        self,
        contact_imports_api: ContactImportsApi,
        import_contacts_params: list[ImportContactParams],
    ) -> None:
        expected_response = {
            "id": IMPORT_ID,
            "status": "started",
        }
        responses.post(
            BASE_CONTACT_IMPORTS_URL,
            json=expected_response,
            status=201,
        )

        contact_import = contact_imports_api.import_contacts(import_contacts_params)

        assert isinstance(contact_import, ContactImport)
        assert contact_import.id == IMPORT_ID
        assert contact_import.status == "started"

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
    def test_get_contact_import_should_raise_api_errors(
        self,
        contact_imports_api: ContactImportsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.get(
            f"{BASE_CONTACT_IMPORTS_URL}/{IMPORT_ID}",
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            contact_imports_api.get_by_id(IMPORT_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_contact_import_should_return_started_import(
        self, contact_imports_api: ContactImportsApi, sample_contact_import_dict: dict
    ) -> None:
        responses.get(
            f"{BASE_CONTACT_IMPORTS_URL}/{IMPORT_ID}",
            json=sample_contact_import_dict,
            status=200,
        )

        contact_import = contact_imports_api.get_by_id(IMPORT_ID)

        assert isinstance(contact_import, ContactImport)
        assert contact_import.id == IMPORT_ID
        assert contact_import.status == "started"

    @responses.activate
    def test_get_contact_import_should_return_finished_import(
        self,
        contact_imports_api: ContactImportsApi,
        sample_finished_contact_import_dict: dict,
    ) -> None:
        responses.get(
            f"{BASE_CONTACT_IMPORTS_URL}/{IMPORT_ID}",
            json=sample_finished_contact_import_dict,
            status=200,
        )

        contact_import = contact_imports_api.get_by_id(IMPORT_ID)

        assert isinstance(contact_import, ContactImport)
        assert contact_import.id == IMPORT_ID
        assert contact_import.status == "finished"
        assert contact_import.created_contacts_count == 1
        assert contact_import.updated_contacts_count == 3
        assert contact_import.contacts_over_limit_count == 3
