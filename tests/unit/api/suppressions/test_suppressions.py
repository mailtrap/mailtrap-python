import json
from datetime import datetime
from typing import Any
from urllib.parse import parse_qs
from urllib.parse import urlparse

import pytest
import responses

from mailtrap.api.resources.suppressions import SuppressionsApi
from mailtrap.config import GENERAL_HOST
from mailtrap.exceptions import APIError
from mailtrap.http import HttpClient
from mailtrap.models.suppressions import CreateSuppressionParams
from mailtrap.models.suppressions import Suppression
from tests import conftest

ACCOUNT_ID = "321"
SUPPRESSION_ID = "supp_123456"
BASE_SUPPRESSIONS_URL = f"https://{GENERAL_HOST}/api/accounts/{ACCOUNT_ID}/suppressions"


@pytest.fixture
def suppressions_api() -> SuppressionsApi:
    return SuppressionsApi(account_id=ACCOUNT_ID, client=HttpClient(GENERAL_HOST))


@pytest.fixture
def sample_suppression_dict() -> dict[str, Any]:
    return {
        "id": SUPPRESSION_ID,
        "type": "unsubscription",
        "created_at": "2024-12-26T09:40:44.161Z",
        "email": "recipient@example.com",
        "sending_stream": "transactional",
        "domain_name": "sender.com",
        "message_bounce_category": None,
        "message_category": "Welcome email",
        "message_client_ip": "123.123.123.123",
        "message_created_at": "2024-12-26T07:10:00.889Z",
        "message_outgoing_ip": "1.1.1.1",
        "message_recipient_mx_name": "Other Providers",
        "message_sender_email": "hello@sender.com",
        "message_subject": "Welcome!",
    }


class TestSuppressionsApi:

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
    def test_get_suppressions_should_raise_api_errors(
        self,
        suppressions_api: SuppressionsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.get(
            BASE_SUPPRESSIONS_URL,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            suppressions_api.get_list()

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_suppressions_should_return_suppression_list(
        self, suppressions_api: SuppressionsApi, sample_suppression_dict: dict
    ) -> None:
        responses.get(
            BASE_SUPPRESSIONS_URL,
            json=[sample_suppression_dict],
            status=200,
        )

        suppressions = suppressions_api.get_list()

        assert isinstance(suppressions, list)
        assert all(isinstance(s, Suppression) for s in suppressions)
        assert suppressions[0].id == SUPPRESSION_ID

    @responses.activate
    def test_get_suppressions_with_email_filter_should_return_filtered_list(
        self, suppressions_api: SuppressionsApi, sample_suppression_dict: dict
    ) -> None:
        email_filter = "recipient@example.com"
        responses.get(
            BASE_SUPPRESSIONS_URL,
            json=[sample_suppression_dict],
            status=200,
            match=[responses.matchers.query_param_matcher({"email": email_filter})],
        )

        suppressions = suppressions_api.get_list(email=email_filter)

        assert isinstance(suppressions, list)
        assert all(isinstance(s, Suppression) for s in suppressions)
        assert suppressions[0].id == SUPPRESSION_ID
        assert suppressions[0].email == email_filter
        assert isinstance(suppressions[0].created_at, datetime)

    @responses.activate
    def test_get_suppressions_should_send_no_query_params_by_default(
        self, suppressions_api: SuppressionsApi, sample_suppression_dict: dict
    ) -> None:
        responses.get(BASE_SUPPRESSIONS_URL, json=[sample_suppression_dict])

        suppressions = suppressions_api.get_list()

        assert urlparse(responses.calls[0].request.url).query == ""
        assert suppressions[0].subscription_topic_id is None

    @responses.activate
    def test_get_suppressions_should_include_topic_unsubscriptions(
        self, suppressions_api: SuppressionsApi, sample_suppression_dict: dict
    ) -> None:
        topic_unsubscription = {
            "id": "supp_654321",
            "type": "topic unsubscription",
            "created_at": "2024-12-27T09:40:44.161Z",
            "email": "recipient@example.com",
            "sending_stream": "bulk",
            "domain_name": "sender.com",
            "subscription_topic_id": 17,
        }
        responses.get(
            BASE_SUPPRESSIONS_URL,
            json=[sample_suppression_dict, topic_unsubscription],
        )

        suppressions = suppressions_api.get_list(include_topic_unsubscriptions=True)

        # The API opts in only on the exact string "true".
        assert parse_qs(urlparse(responses.calls[0].request.url).query) == {
            "include_topic_unsubscriptions": ["true"]
        }
        assert suppressions[1].type == "topic unsubscription"
        assert suppressions[1].domain_name == "sender.com"
        assert suppressions[1].subscription_topic_id == 17

    @responses.activate
    def test_get_suppressions_should_send_email_with_topic_unsubscriptions(
        self, suppressions_api: SuppressionsApi
    ) -> None:
        responses.get(BASE_SUPPRESSIONS_URL, json=[])

        suppressions_api.get_list(
            email="recipient@example.com", include_topic_unsubscriptions=True
        )

        assert parse_qs(urlparse(responses.calls[0].request.url).query) == {
            "email": ["recipient@example.com"],
            "include_topic_unsubscriptions": ["true"],
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
    def test_delete_suppression_should_raise_api_errors(
        self,
        suppressions_api: SuppressionsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.delete(
            f"{BASE_SUPPRESSIONS_URL}/{SUPPRESSION_ID}",
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            suppressions_api.delete(SUPPRESSION_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_delete_suppression_should_return_deleted_suppression(
        self, suppressions_api: SuppressionsApi, sample_suppression_dict: dict
    ) -> None:
        responses.delete(
            f"{BASE_SUPPRESSIONS_URL}/{SUPPRESSION_ID}",
            json=sample_suppression_dict,
            status=200,
        )

        deleted_suppression = suppressions_api.delete(SUPPRESSION_ID)

        assert isinstance(deleted_suppression, Suppression)
        assert deleted_suppression.id == SUPPRESSION_ID
        assert deleted_suppression.type == "unsubscription"
        assert deleted_suppression.email == "recipient@example.com"
        assert deleted_suppression.sending_stream == "transactional"

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
                {"errors": "Email is invalid"},
                "Email is invalid",
            ),
            (
                conftest.RATE_LIMIT_ERROR_STATUS_CODE,
                conftest.RATE_LIMIT_ERROR_RESPONSE,
                conftest.RATE_LIMIT_ERROR_MESSAGE,
            ),
        ],
    )
    @responses.activate
    def test_create_suppression_should_raise_api_errors(
        self,
        suppressions_api: SuppressionsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.post(
            BASE_SUPPRESSIONS_URL,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            suppressions_api.create(
                CreateSuppressionParams(
                    email="recipient@example.com",
                    domain_id=12345,
                    sending_stream="transactional",
                )
            )

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_create_suppression_should_send_flat_body_and_unwrap_data(
        self, suppressions_api: SuppressionsApi, sample_suppression_dict: dict
    ) -> None:
        responses.post(
            BASE_SUPPRESSIONS_URL,
            json={"data": sample_suppression_dict},
            status=201,
        )

        suppression = suppressions_api.create(
            CreateSuppressionParams(
                email="recipient@example.com",
                domain_id=12345,
                sending_stream="transactional",
            )
        )

        assert isinstance(suppression, Suppression)
        assert suppression.id == SUPPRESSION_ID
        assert json.loads(responses.calls[0].request.body) == {
            "email": "recipient@example.com",
            "domain_id": 12345,
            "sending_stream": "transactional",
        }

    @responses.activate
    def test_create_suppression_should_send_type_when_provided(
        self, suppressions_api: SuppressionsApi, sample_suppression_dict: dict
    ) -> None:
        responses.post(
            BASE_SUPPRESSIONS_URL,
            json={"data": sample_suppression_dict},
            status=201,
        )

        suppressions_api.create(
            CreateSuppressionParams(
                email="recipient@example.com",
                domain_id=12345,
                sending_stream="bulk",
                type="spam complaint",
            )
        )

        assert json.loads(responses.calls[0].request.body) == {
            "email": "recipient@example.com",
            "domain_id": 12345,
            "sending_stream": "bulk",
            "type": "spam complaint",
        }
