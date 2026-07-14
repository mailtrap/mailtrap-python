from typing import Any

import pytest
import responses

from mailtrap.api.resources.contact_lists import ContactListsApi
from mailtrap.config import GENERAL_HOST
from mailtrap.exceptions import APIError
from mailtrap.http import HttpClient
from mailtrap.models.common import DeletedObject
from mailtrap.models.contacts import ContactList
from mailtrap.models.contacts import ContactListParams
from tests import conftest

ACCOUNT_ID = "321"
LIST_ID = 1234
BASE_CONTACT_LISTS_URL = (
    f"https://{GENERAL_HOST}/api/accounts/{ACCOUNT_ID}/contacts/lists"
)


@pytest.fixture
def contact_lists_api() -> ContactListsApi:
    return ContactListsApi(account_id=ACCOUNT_ID, client=HttpClient(GENERAL_HOST))


@pytest.fixture
def sample_contact_list_dict() -> dict[str, Any]:
    return {
        "id": LIST_ID,
        "name": "My Contact List",
    }


@pytest.fixture
def create_contact_list_params() -> ContactListParams:
    return ContactListParams(name="My Contact List")


@pytest.fixture
def update_contact_list_params() -> ContactListParams:
    return ContactListParams(name="Updated Contact List")


class TestContactListsApi:

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
                conftest.RATE_LIMIT_ERROR_STATUS_CODE,
                conftest.RATE_LIMIT_ERROR_RESPONSE,
                conftest.RATE_LIMIT_ERROR_MESSAGE,
            ),
            (
                conftest.INTERNAL_SERVER_ERROR_STATUS_CODE,
                conftest.INTERNAL_SERVER_ERROR_RESPONSE,
                conftest.INTERNAL_SERVER_ERROR_MESSAGE,
            ),
        ],
    )
    @responses.activate
    def test_get_contact_lists_should_raise_api_errors(
        self,
        contact_lists_api: ContactListsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.get(
            BASE_CONTACT_LISTS_URL,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            contact_lists_api.get_list()

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_contact_lists_should_return_contact_list_list(
        self, contact_lists_api: ContactListsApi, sample_contact_list_dict: dict
    ) -> None:
        responses.get(
            BASE_CONTACT_LISTS_URL,
            json=[sample_contact_list_dict],
            status=200,
        )

        contact_lists = contact_lists_api.get_list()

        assert isinstance(contact_lists, list)
        assert all(
            isinstance(contact_list, ContactList) for contact_list in contact_lists
        )
        assert contact_lists[0].id == LIST_ID

    @responses.activate
    def test_get_contact_lists_with_search_should_filter_by_name(
        self, contact_lists_api: ContactListsApi, sample_contact_list_dict: dict
    ) -> None:
        search = "news"
        responses.get(
            BASE_CONTACT_LISTS_URL,
            json=[sample_contact_list_dict],
            status=200,
            match=[responses.matchers.query_param_matcher({"search": search})],
        )

        contact_lists = contact_lists_api.get_list(search=search)

        assert isinstance(contact_lists, list)
        assert contact_lists[0].id == LIST_ID
        assert responses.calls[0].request.params["search"] == search

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
            (
                conftest.RATE_LIMIT_ERROR_STATUS_CODE,
                conftest.RATE_LIMIT_ERROR_RESPONSE,
                conftest.RATE_LIMIT_ERROR_MESSAGE,
            ),
            (
                conftest.INTERNAL_SERVER_ERROR_STATUS_CODE,
                conftest.INTERNAL_SERVER_ERROR_RESPONSE,
                conftest.INTERNAL_SERVER_ERROR_MESSAGE,
            ),
        ],
    )
    @responses.activate
    def test_get_contact_list_should_raise_api_errors(
        self,
        contact_lists_api: ContactListsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.get(
            f"{BASE_CONTACT_LISTS_URL}/{LIST_ID}",
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            contact_lists_api.get_by_id(LIST_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_contact_list_should_return_contact_list(
        self, contact_lists_api: ContactListsApi, sample_contact_list_dict: dict
    ) -> None:
        responses.get(
            f"{BASE_CONTACT_LISTS_URL}/{LIST_ID}",
            json=sample_contact_list_dict,
            status=200,
        )

        contact_list = contact_lists_api.get_by_id(LIST_ID)

        assert isinstance(contact_list, ContactList)
        assert contact_list.id == LIST_ID
        assert contact_list.name == "My Contact List"

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
                conftest.RATE_LIMIT_ERROR_STATUS_CODE,
                conftest.RATE_LIMIT_ERROR_RESPONSE,
                conftest.RATE_LIMIT_ERROR_MESSAGE,
            ),
            (
                conftest.INTERNAL_SERVER_ERROR_STATUS_CODE,
                conftest.INTERNAL_SERVER_ERROR_RESPONSE,
                conftest.INTERNAL_SERVER_ERROR_MESSAGE,
            ),
        ],
    )
    @responses.activate
    def test_create_contact_list_should_raise_api_errors(
        self,
        contact_lists_api: ContactListsApi,
        create_contact_list_params: ContactListParams,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.post(
            BASE_CONTACT_LISTS_URL,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            contact_lists_api.create(create_contact_list_params)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_create_contact_list_should_return_created_contact_list(
        self,
        contact_lists_api: ContactListsApi,
        create_contact_list_params: ContactListParams,
    ) -> None:
        expected_response = {
            "id": LIST_ID,
            "name": "My Contact List",
        }
        responses.post(
            BASE_CONTACT_LISTS_URL,
            json=expected_response,
            status=201,
        )

        contact_list = contact_lists_api.create(create_contact_list_params)

        assert isinstance(contact_list, ContactList)
        assert contact_list.id == LIST_ID
        assert contact_list.name == "My Contact List"

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
            (
                conftest.RATE_LIMIT_ERROR_STATUS_CODE,
                conftest.RATE_LIMIT_ERROR_RESPONSE,
                conftest.RATE_LIMIT_ERROR_MESSAGE,
            ),
            (
                conftest.INTERNAL_SERVER_ERROR_STATUS_CODE,
                conftest.INTERNAL_SERVER_ERROR_RESPONSE,
                conftest.INTERNAL_SERVER_ERROR_MESSAGE,
            ),
        ],
    )
    @responses.activate
    def test_update_contact_list_should_raise_api_errors(
        self,
        contact_lists_api: ContactListsApi,
        update_contact_list_params: ContactListParams,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.patch(
            f"{BASE_CONTACT_LISTS_URL}/{LIST_ID}",
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            contact_lists_api.update(LIST_ID, update_contact_list_params)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_update_contact_list_should_return_updated_contact_list(
        self,
        contact_lists_api: ContactListsApi,
        update_contact_list_params: ContactListParams,
    ) -> None:
        expected_response = {
            "id": LIST_ID,
            "name": "Updated Contact List",
        }
        responses.patch(
            f"{BASE_CONTACT_LISTS_URL}/{LIST_ID}",
            json=expected_response,
            status=200,
        )

        contact_list = contact_lists_api.update(LIST_ID, update_contact_list_params)

        assert isinstance(contact_list, ContactList)
        assert contact_list.id == LIST_ID
        assert contact_list.name == "Updated Contact List"

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
            (
                conftest.RATE_LIMIT_ERROR_STATUS_CODE,
                conftest.RATE_LIMIT_ERROR_RESPONSE,
                conftest.RATE_LIMIT_ERROR_MESSAGE,
            ),
            (
                conftest.INTERNAL_SERVER_ERROR_STATUS_CODE,
                conftest.INTERNAL_SERVER_ERROR_RESPONSE,
                conftest.INTERNAL_SERVER_ERROR_MESSAGE,
            ),
        ],
    )
    @responses.activate
    def test_delete_contact_list_should_raise_api_errors(
        self,
        contact_lists_api: ContactListsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.delete(
            f"{BASE_CONTACT_LISTS_URL}/{LIST_ID}",
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            contact_lists_api.delete(LIST_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_delete_contact_list_should_return_deleted_object(
        self, contact_lists_api: ContactListsApi
    ) -> None:
        responses.delete(
            f"{BASE_CONTACT_LISTS_URL}/{LIST_ID}",
            status=204,
        )

        deleted_object = contact_lists_api.delete(LIST_ID)

        assert isinstance(deleted_object, DeletedObject)
        assert deleted_object.id == LIST_ID
