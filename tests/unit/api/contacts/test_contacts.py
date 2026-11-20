import json
from typing import Any

import pytest
import responses

from mailtrap.api.resources.contacts import ContactsApi
from mailtrap.config import GENERAL_HOST
from mailtrap.exceptions import APIError
from mailtrap.http import HttpClient
from mailtrap.models.common import DeletedObject
from mailtrap.models.contacts import Contact
from mailtrap.models.contacts import ContactSubscriptionTopic
from mailtrap.models.contacts import CreateContactParams
from mailtrap.models.contacts import UpdateContactParams
from tests import conftest

ACCOUNT_ID = "321"
CONTACT_ID = "018dd5e3-f6d2-7c00-8f9b-e5c3f2d8a132"
BASE_CONTACTS_URL = f"https://{GENERAL_HOST}/api/accounts/{ACCOUNT_ID}/contacts"
TOPIC_ID = 17
DOMAIN_ID = 4321
TOPICS_UNAVAILABLE_RESPONSE = {
    "errors": {"subscription_topics": ["are not available for this account"]}
}
TOPICS_NOT_SAVED_MESSAGE = (
    "The contact was saved, but its subscription topic preferences were not. "
    f"Send them again in an update of contact {CONTACT_ID}."
)


@pytest.fixture
def contacts_api() -> ContactsApi:
    return ContactsApi(account_id=ACCOUNT_ID, client=HttpClient(GENERAL_HOST))


@pytest.fixture
def sample_contact_dict() -> dict[str, Any]:
    return {
        "data": {
            "id": CONTACT_ID,
            "status": "subscribed",
            "email": "john.smith@example.com",
            "fields": {"first_name": "John", "last_name": "Smith"},
            "list_ids": [1, 2, 3],
            "created_at": 1742820600230,
            "updated_at": 1742820600230,
        }
    }


@pytest.fixture
def create_contact_params() -> CreateContactParams:
    return CreateContactParams(
        email="john.smith@example.com",
        fields={"first_name": "John", "last_name": "Smith"},
        list_ids=[1, 2, 3],
    )


@pytest.fixture
def update_contact_params() -> UpdateContactParams:
    return UpdateContactParams(
        email="john.updated@example.com",
        fields={"first_name": "John Updated", "last_name": "Smith Updated"},
    )


class TestContactstApi:

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
    def test_get_contact_should_raise_api_errors(
        self,
        contacts_api: ContactsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.get(
            f"{BASE_CONTACTS_URL}/{CONTACT_ID}",
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            contacts_api.get_by_id(CONTACT_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_contact_should_return_contact(
        self, contacts_api: ContactsApi, sample_contact_dict: dict
    ) -> None:
        responses.get(
            f"{BASE_CONTACTS_URL}/{CONTACT_ID}",
            json=sample_contact_dict,
            status=200,
        )

        contact = contacts_api.get_by_id(CONTACT_ID)

        assert isinstance(contact, Contact)
        assert contact.id == CONTACT_ID
        assert contact.email == "john.smith@example.com"
        assert contact.status == "subscribed"
        assert contact.fields["first_name"] == "John"
        assert contact.fields["last_name"] == "Smith"
        assert contact.list_ids == [1, 2, 3]
        # The account has no subscription topics: the key is absent.
        assert contact.subscription_topics is None

    @pytest.mark.parametrize(
        "subscription_topics,expected",
        [
            (
                [
                    {
                        "subscription_topic_id": TOPIC_ID,
                        "domain_id": DOMAIN_ID,
                        "status": "unsubscribed",
                    },
                    {
                        "subscription_topic_id": 18,
                        "domain_id": DOMAIN_ID,
                        "status": "subscribed",
                    },
                ],
                [
                    ContactSubscriptionTopic(
                        subscription_topic_id=TOPIC_ID,
                        domain_id=DOMAIN_ID,
                        status="unsubscribed",
                    ),
                    ContactSubscriptionTopic(
                        subscription_topic_id=18,
                        domain_id=DOMAIN_ID,
                        status="subscribed",
                    ),
                ],
            ),
            # The preferences couldn't be read.
            (None, None),
        ],
    )
    @responses.activate
    def test_get_contact_should_return_subscription_topics(
        self,
        contacts_api: ContactsApi,
        sample_contact_dict: dict,
        subscription_topics: Any,
        expected: Any,
    ) -> None:
        sample_contact_dict["data"]["subscription_topics"] = subscription_topics
        responses.get(
            f"{BASE_CONTACTS_URL}/{CONTACT_ID}",
            json=sample_contact_dict,
            status=200,
        )

        contact = contacts_api.get_by_id(CONTACT_ID)

        assert contact.subscription_topics == expected

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
            (
                409,
                {"errors": "Contact exists"},
                "Contact exists",
            ),
            (
                422,
                {"errors": {"email": ["Email is invalid"]}},
                "Email is invalid",
            ),
            (
                conftest.VALIDATION_ERRORS_STATUS_CODE,
                TOPICS_UNAVAILABLE_RESPONSE,
                "subscription_topics: are not available for this account",
            ),
            (
                503,
                {"errors": TOPICS_NOT_SAVED_MESSAGE},
                TOPICS_NOT_SAVED_MESSAGE,
            ),
        ],
    )
    @responses.activate
    def test_create_contact_should_raise_api_errors(
        self,
        contacts_api: ContactsApi,
        create_contact_params: CreateContactParams,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.post(
            BASE_CONTACTS_URL,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            contacts_api.create(create_contact_params)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_create_contact_should_return_created_contact(
        self,
        contacts_api: ContactsApi,
        create_contact_params: CreateContactParams,
    ) -> None:
        expected_response = {
            "data": {
                "id": CONTACT_ID,
                "status": "subscribed",
                "email": "john.smith@example.com",
                "fields": {"first_name": "John", "last_name": "Smith"},
                "list_ids": [1, 2, 3],
                "created_at": 1742820600230,
                "updated_at": 1742820600230,
            }
        }
        responses.post(
            BASE_CONTACTS_URL,
            json=expected_response,
            status=201,
        )

        contact = contacts_api.create(create_contact_params)

        assert isinstance(contact, Contact)
        assert contact.id == CONTACT_ID
        assert contact.email == "john.smith@example.com"
        assert contact.status == "subscribed"
        assert contact.fields["first_name"] == "John"
        assert contact.fields["last_name"] == "Smith"
        assert contact.list_ids == [1, 2, 3]

    @responses.activate
    def test_create_contact_should_send_subscription_topics(
        self, contacts_api: ContactsApi, sample_contact_dict: dict
    ) -> None:
        topic = {
            "subscription_topic_id": TOPIC_ID,
            "domain_id": DOMAIN_ID,
            "status": "unsubscribed",
        }
        sample_contact_dict["data"]["subscription_topics"] = [topic]
        responses.post(BASE_CONTACTS_URL, json=sample_contact_dict, status=201)

        contact = contacts_api.create(
            CreateContactParams(
                email="john.smith@example.com",
                subscription_topics=[ContactSubscriptionTopic(**topic)],
            )
        )

        assert json.loads(responses.calls[0].request.body) == {
            "contact": {
                "email": "john.smith@example.com",
                "subscription_topics": [topic],
            }
        }
        assert contact.subscription_topics == [ContactSubscriptionTopic(**topic)]

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
            (
                409,
                {"errors": "Contact exists"},
                "Contact exists",
            ),
            (
                conftest.VALIDATION_ERRORS_STATUS_CODE,
                {"errors": {"email": [["is invalid"]], "birthdate": [["is invalid"]]}},
                "email: ['is invalid']; birthdate: ['is invalid']",
            ),
            (
                conftest.VALIDATION_ERRORS_STATUS_CODE,
                TOPICS_UNAVAILABLE_RESPONSE,
                "subscription_topics: are not available for this account",
            ),
            (
                503,
                {"errors": TOPICS_NOT_SAVED_MESSAGE},
                TOPICS_NOT_SAVED_MESSAGE,
            ),
        ],
    )
    @responses.activate
    def test_update_contact_should_raise_api_errors(
        self,
        contacts_api: ContactsApi,
        update_contact_params: UpdateContactParams,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.patch(
            f"{BASE_CONTACTS_URL}/{CONTACT_ID}",
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            contacts_api.update(CONTACT_ID, update_contact_params)
        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_update_contact_should_return_updated_contact(
        self,
        contacts_api: ContactsApi,
        update_contact_params: UpdateContactParams,
    ) -> None:
        expected_response = {
            "data": {
                "id": CONTACT_ID,
                "status": "subscribed",
                "email": "john.updated@example.com",
                "fields": {"first_name": "John Updated", "last_name": "Smith Updated"},
                "list_ids": [1, 2, 3],
                "created_at": 1742820600230,
                "updated_at": 1742820600230,
            }
        }
        responses.patch(
            f"{BASE_CONTACTS_URL}/{CONTACT_ID}",
            json=expected_response,
            status=200,
        )

        contact = contacts_api.update(CONTACT_ID, update_contact_params)

        assert isinstance(contact, Contact)
        assert contact.id == CONTACT_ID
        assert contact.email == "john.updated@example.com"
        assert contact.status == "subscribed"
        assert contact.fields["first_name"] == "John Updated"
        assert contact.fields["last_name"] == "Smith Updated"

    @responses.activate
    def test_update_contact_should_send_only_subscription_topics(
        self, contacts_api: ContactsApi, sample_contact_dict: dict
    ) -> None:
        topic = {
            "subscription_topic_id": TOPIC_ID,
            "domain_id": DOMAIN_ID,
            "status": "subscribed",
        }
        sample_contact_dict["data"]["subscription_topics"] = [topic]
        responses.patch(
            f"{BASE_CONTACTS_URL}/{CONTACT_ID}", json=sample_contact_dict, status=200
        )

        contact = contacts_api.update(
            CONTACT_ID,
            UpdateContactParams(subscription_topics=[ContactSubscriptionTopic(**topic)]),
        )

        assert json.loads(responses.calls[0].request.body) == {
            "contact": {"subscription_topics": [topic]}
        }
        assert contact.subscription_topics == [ContactSubscriptionTopic(**topic)]

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
    def test_delete_contact_should_raise_api_errors(
        self,
        contacts_api: ContactsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.delete(
            f"{BASE_CONTACTS_URL}/{CONTACT_ID}",
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            contacts_api.delete(CONTACT_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_delete_contact_should_return_deleted_object(
        self, contacts_api: ContactsApi
    ) -> None:
        responses.delete(
            f"{BASE_CONTACTS_URL}/{CONTACT_ID}",
            status=204,
        )

        deleted_object = contacts_api.delete(CONTACT_ID)

        assert isinstance(deleted_object, DeletedObject)
        assert deleted_object.id == CONTACT_ID
