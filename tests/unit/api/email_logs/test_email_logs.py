"""Unit tests for Email Logs API."""

from typing import Any

import pytest
import responses

from mailtrap.api.resources.email_logs import EmailLogsApi
from mailtrap.config import GENERAL_HOST
from mailtrap.exceptions import APIError
from mailtrap.http import HttpClient
from mailtrap.models.email_logs import EmailLogMessage
from mailtrap.models.email_logs import EmailLogsListFilters
from tests import conftest

ACCOUNT_ID = "321"
MESSAGE_ID = "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
BASE_EMAIL_LOGS_URL = f"https://{GENERAL_HOST}/api/accounts/{ACCOUNT_ID}/email_logs"


@pytest.fixture
def email_logs_api() -> EmailLogsApi:
    return EmailLogsApi(client=HttpClient(GENERAL_HOST), account_id=ACCOUNT_ID)


@pytest.fixture
def sample_message_dict() -> dict[str, Any]:
    return {
        "message_id": MESSAGE_ID,
        "status": "delivered",
        "subject": "Welcome",
        "from": "sender@example.com",
        "to": "recipient@example.com",
        "sent_at": "2025-01-15T10:30:00Z",
        "client_ip": "203.0.113.42",
        "category": "Welcome Email",
        "custom_variables": {},
        "sending_stream": "transactional",
        "sending_domain_id": 3938,
        "template_id": 100,
        "template_variables": {},
        "opens_count": 2,
        "clicks_count": 1,
    }


@pytest.fixture
def sample_list_response(sample_message_dict: dict[str, Any]) -> dict[str, Any]:
    return {
        "messages": [sample_message_dict],
        "total_count": 1,
        "next_page_cursor": None,
    }


@pytest.fixture
def sample_message_detail(sample_message_dict: dict[str, Any]) -> dict[str, Any]:
    detail = dict(sample_message_dict)
    detail["raw_message_url"] = "https://storage.example.com/signed/eml/..."
    detail["events"] = [
        {
            "event_type": "click",
            "created_at": "2025-01-15T10:35:00Z",
            "details": {
                "click_url": "https://example.com/track/abc",
                "web_ip_address": "198.51.100.50",
            },
        },
    ]
    return detail


class TestEmailLogsApi:
    @responses.activate
    def test_get_list_returns_response(
        self,
        email_logs_api: EmailLogsApi,
        sample_list_response: dict[str, Any],
    ) -> None:
        responses.get(BASE_EMAIL_LOGS_URL, json=sample_list_response, status=200)

        result = email_logs_api.get_list()

        assert result.total_count == 1
        assert result.next_page_cursor is None
        assert len(result.messages) == 1
        msg = result.messages[0]
        assert isinstance(msg, EmailLogMessage)
        assert msg.message_id == MESSAGE_ID
        assert msg.status == "delivered"
        assert msg.from_ == "sender@example.com"
        assert msg.to == "recipient@example.com"
        assert msg.opens_count == 2
        assert msg.clicks_count == 1

    @responses.activate
    def test_get_list_with_filters_and_search_after(
        self,
        email_logs_api: EmailLogsApi,
        sample_list_response: dict[str, Any],
    ) -> None:
        filters = EmailLogsListFilters(
            sent_after="2025-01-01T00:00:00Z",
            sent_before="2025-01-31T23:59:59Z",
            to={"operator": "ci_equal", "value": "recipient@example.com"},
        )
        responses.get(
            BASE_EMAIL_LOGS_URL,
            json=sample_list_response,
            status=200,
        )

        result = email_logs_api.get_list(filters=filters, search_after="b2c3")

        assert result.total_count == 1
        assert len(result.messages) == 1
        assert result.messages[0].message_id == MESSAGE_ID

    @responses.activate
    def test_get_by_id_returns_sending_message(
        self,
        email_logs_api: EmailLogsApi,
        sample_message_detail: dict[str, Any],
    ) -> None:
        responses.get(
            f"{BASE_EMAIL_LOGS_URL}/{MESSAGE_ID}",
            json=sample_message_detail,
            status=200,
        )

        msg = email_logs_api.get_by_id(MESSAGE_ID)

        assert isinstance(msg, EmailLogMessage)
        assert msg.message_id == MESSAGE_ID
        assert msg.from_ == "sender@example.com"
        assert msg.raw_message_url is not None
        assert len(msg.events) == 1
        assert msg.events[0].event_type == "click"

    @responses.activate
    def test_get_list_treats_non_dict_response_as_empty(
        self,
        email_logs_api: EmailLogsApi,
    ) -> None:
        """200 with JSON array (or other non-object) must not call .get on a non-dict."""
        responses.get(BASE_EMAIL_LOGS_URL, json=[], status=200)

        result = email_logs_api.get_list()

        assert result.messages == []
        assert result.total_count == 0
        assert result.next_page_cursor is None

    @responses.activate
    def test_get_list_empty_body_returns_empty(
        self,
        email_logs_api: EmailLogsApi,
    ) -> None:
        """Empty 200 body yields None from HttpClient; list response stays safe."""
        responses.get(BASE_EMAIL_LOGS_URL, body="", status=200)

        result = email_logs_api.get_list()

        assert result.messages == []
        assert result.total_count == 0
        assert result.next_page_cursor is None

    @responses.activate
    def test_get_by_id_non_dict_raises_value_error(
        self,
        email_logs_api: EmailLogsApi,
    ) -> None:
        responses.get(
            f"{BASE_EMAIL_LOGS_URL}/{MESSAGE_ID}",
            json=["unexpected"],
            status=200,
        )

        with pytest.raises(ValueError, match=MESSAGE_ID) as exc_info:
            email_logs_api.get_by_id(MESSAGE_ID)

        assert "list" in str(exc_info.value)

    @pytest.mark.parametrize(
        "status_code,response_json,expected_error_message",
        [
            (
                conftest.UNAUTHORIZED_STATUS_CODE,
                conftest.UNAUTHORIZED_RESPONSE,
                conftest.UNAUTHORIZED_ERROR_MESSAGE,
            ),
            (
                conftest.NOT_FOUND_STATUS_CODE,
                conftest.NOT_FOUND_RESPONSE,
                conftest.NOT_FOUND_ERROR_MESSAGE,
            ),
        ],
    )
    @responses.activate
    def test_get_list_raises_api_errors(
        self,
        email_logs_api: EmailLogsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.get(BASE_EMAIL_LOGS_URL, status=status_code, json=response_json)

        with pytest.raises(APIError) as exc_info:
            email_logs_api.get_list()

        assert expected_error_message in str(exc_info.value)

    @pytest.mark.parametrize(
        "status_code,response_json,expected_error_message",
        [
            (
                conftest.UNAUTHORIZED_STATUS_CODE,
                conftest.UNAUTHORIZED_RESPONSE,
                conftest.UNAUTHORIZED_ERROR_MESSAGE,
            ),
            (
                conftest.NOT_FOUND_STATUS_CODE,
                conftest.NOT_FOUND_RESPONSE,
                conftest.NOT_FOUND_ERROR_MESSAGE,
            ),
        ],
    )
    @responses.activate
    def test_get_by_id_raises_api_errors(
        self,
        email_logs_api: EmailLogsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.get(
            f"{BASE_EMAIL_LOGS_URL}/{MESSAGE_ID}",
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            email_logs_api.get_by_id(MESSAGE_ID)

        assert expected_error_message in str(exc_info.value)
