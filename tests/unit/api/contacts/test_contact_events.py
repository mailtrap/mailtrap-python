from typing import Any

import pytest
import responses

from mailtrap.api.resources.contact_events import ContactEventsApi
from mailtrap.config import GENERAL_HOST
from mailtrap.exceptions import APIError
from mailtrap.http import HttpClient
from mailtrap.models.contacts import ContactEvent
from mailtrap.models.contacts import ContactEventParams
from tests import conftest

ACCOUNT_ID = "321"
EXPORT_ID = 1
CONTACT_IDENTIFIER = "d82d0d9e-bbb7-4656-a591-e64682bffae7"
BASE_CONTACT_EVENTS_URL = (
    f"https://{GENERAL_HOST}/api/accounts/{ACCOUNT_ID}"
    f"/contacts/{CONTACT_IDENTIFIER}/events"
)


@pytest.fixture
def client() -> ContactEventsApi:
    return ContactEventsApi(account_id=ACCOUNT_ID, client=HttpClient(GENERAL_HOST))


@pytest.fixture
def sample_contact_event_dict() -> dict[str, Any]:
    return {
        "contact_id": CONTACT_IDENTIFIER,
        "contact_email": "test-email@gmail.com",
        "name": "UserLogin",
        "params": {
            "user_id": 101,
            "user_name": "John Smith",
            "is_active": True,
            "last_seen": None,
        },
    }


@pytest.fixture
def sample_create_contact_event_params() -> ContactEventParams:
    return ContactEventParams(
        name="UserLogin",
        params={
            "user_id": 101,
            "user_name": "John Smith",
            "is_active": True,
            "last_seen": None,
        },
    )


class TestContactEventsApi:

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
            (
                422,
                {
                    "errors": {
                        "name": [["must be a string", "is too long"]],
                        "params": [
                            [
                                "must be a hash",
                                "key 'foo' is too long",
                                "value for 'bar' is too long",
                            ]
                        ],
                    }
                },
                (
                    "name: ['must be a string', 'is too long']; "
                    "params: ['must be a hash', \"key 'foo' is too long\", "
                    "\"value for 'bar' is too long\"]"
                ),
            ),
        ],
    )
    @responses.activate
    def test_create_should_raise_api_errors(
        self,
        client: ContactEventsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
        sample_create_contact_event_params: ContactEventParams,
    ) -> None:
        responses.post(
            BASE_CONTACT_EVENTS_URL,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.create(CONTACT_IDENTIFIER, sample_create_contact_event_params)

        print(str(exc_info.value))

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_create_should_return_contact_event(
        self,
        client: ContactEventsApi,
        sample_contact_event_dict: dict,
        sample_create_contact_event_params: ContactEventParams,
    ) -> None:
        responses.post(
            BASE_CONTACT_EVENTS_URL,
            json=sample_contact_event_dict,
            status=201,
        )

        result = client.create(CONTACT_IDENTIFIER, sample_create_contact_event_params)

        assert isinstance(result, ContactEvent)
        assert result.contact_id == CONTACT_IDENTIFIER
        assert result.contact_email == "test-email@gmail.com"
        assert result.name == "UserLogin"
        request = responses.calls[0].request
        assert request.url == BASE_CONTACT_EVENTS_URL
