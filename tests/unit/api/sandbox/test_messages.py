from typing import Any

import pytest
import responses

from mailtrap.api.resources.messages import MessagesApi
from mailtrap.config import GENERAL_HOST
from mailtrap.exceptions import APIError
from mailtrap.http import HttpClient
from mailtrap.models.messages import EmailMessage
from mailtrap.models.messages import UpdateEmailMessageParams
from tests import conftest

ACCOUNT_ID = "321"
INBOX_ID = 3538
MESSAGE_ID = 2323
ATTACHMENT_ID = 67
BASE_MESSAGES_URL = (
    f"https://{GENERAL_HOST}/api/accounts/{ACCOUNT_ID}/inboxes/{INBOX_ID}/messages"
)


@pytest.fixture
def client() -> MessagesApi:
    return MessagesApi(account_id=ACCOUNT_ID, client=HttpClient(GENERAL_HOST))


@pytest.fixture
def sample_message_dict() -> dict[str, Any]:
    return {
        "id": MESSAGE_ID,
        "inbox_id": INBOX_ID,
        "subject": "Test email",
        "sent_at": "2022-07-01T19:29:59.295Z",
        "from_email": "john@mailtrap.io",
        "from_name": "John",
        "to_email": "mary@mailtrap.io",
        "to_name": "Mary",
        "email_size": 300,
        "is_read": False,
        "created_at": "2022-07-01T19:29:59.295Z",
        "updated_at": "2022-07-01T19:29:59.295Z",
        "html_body_size": 150,
        "text_body_size": 100,
        "human_size": "300 Bytes",
        "html_path": (
            f"/api/accounts/{ACCOUNT_ID}"
            f"/inboxes/{INBOX_ID}"
            f"/messages/{MESSAGE_ID}/body.html"
        ),
        "txt_path": (
            f"/api/accounts/{ACCOUNT_ID}"
            f"/inboxes/{INBOX_ID}"
            f"/messages/{MESSAGE_ID}/body.txt"
        ),
        "raw_path": (
            f"/api/accounts/{ACCOUNT_ID}"
            f"/inboxes/{INBOX_ID}"
            f"/messages/{MESSAGE_ID}/body.raw"
        ),
        "download_path": (
            f"/api/accounts/{ACCOUNT_ID}"
            f"/inboxes/{INBOX_ID}"
            f"/messages/{MESSAGE_ID}/body.eml"
        ),
        "html_source_path": (
            f"/api/accounts/{ACCOUNT_ID}"
            f"/inboxes/{INBOX_ID}"
            f"/messages/{MESSAGE_ID}/body.htmlsource"
        ),
        "blacklists_report_info": False,
        "smtp_information": {
            "ok": True,
            "data": {"mail_from_addr": "john@mailtrap.io", "client_ip": "193.62.62.184"},
        },
    }


@pytest.fixture
def sample_spam_report_dict() -> dict[str, Any]:
    return {
        "report": {
            "ResponseCode": 2,
            "ResponseMessage": "Not spam",
            "ResponseVersion": "1.2",
            "Score": 1.2,
            "Spam": False,
            "Threshold": 5,
            "Details": [
                {
                    "Pts": 0,
                    "RuleName": "HTML_MESSAGE",
                    "Description": "BODY: HTML included in message",
                }
            ],
        }
    }


@pytest.fixture
def sample_html_analysis_dict() -> dict[str, Any]:
    return {
        "report": {
            "status": "success",
            "errors": [
                {
                    "error_line": 15,
                    "rule_name": "style",
                    "email_clients": {
                        "desktop": ["Notes 6 / 7"],
                        "mobile": ["Gmail"],
                        "web": [],
                    },
                }
            ],
        }
    }


@pytest.fixture
def sample_forwarded_message_dict() -> dict[str, Any]:
    return {"message": "Your email message has been successfully forwarded"}


@pytest.fixture
def sample_mail_headers_dict() -> dict[str, Any]:
    return {
        "headers": {
            "bcc": "john_doe@example.com",
            "cc": "john_doe@example.com",
            "from": "john_doe@example.com",
            "to": "john_doe@example.com",
            "subject": "Your Example Order Confirmation",
        }
    }


class TestMessagesApi:

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
        client: MessagesApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.get(
            BASE_MESSAGES_URL,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.get_list(INBOX_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_list_should_return_message_list(
        self, client: MessagesApi, sample_message_dict: dict
    ) -> None:
        responses.get(
            BASE_MESSAGES_URL,
            json=[sample_message_dict],
            status=200,
        )

        messages = client.get_list(INBOX_ID)

        assert isinstance(messages, list)
        assert all(isinstance(m, EmailMessage) for m in messages)
        assert messages[0].id == MESSAGE_ID

    @responses.activate
    def test_get_list_with_params_should_include_query_params(
        self, client: MessagesApi, sample_message_dict: dict
    ) -> None:
        responses.get(
            BASE_MESSAGES_URL,
            json=[sample_message_dict],
            status=200,
        )

        client.get_list(INBOX_ID, search="welcome", last_id=123, page=5)

        assert len(responses.calls) == 1
        request = responses.calls[0].request
        assert "search=welcome" in request.url
        assert "last_id=123" in request.url
        assert "page=5" in request.url

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
    def test_show_message_should_raise_api_errors(
        self,
        client: MessagesApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        url = f"{BASE_MESSAGES_URL}/{MESSAGE_ID}"
        responses.get(
            url,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.show_message(INBOX_ID, MESSAGE_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_show_message_should_return_single_message(
        self, client: MessagesApi, sample_message_dict: dict
    ) -> None:
        url = f"{BASE_MESSAGES_URL}/{MESSAGE_ID}"
        responses.get(
            url,
            json=sample_message_dict,
            status=200,
        )

        message = client.show_message(INBOX_ID, MESSAGE_ID)

        assert isinstance(message, EmailMessage)
        assert message.id == MESSAGE_ID

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
        client: MessagesApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        url = f"{BASE_MESSAGES_URL}/{MESSAGE_ID}"
        responses.patch(
            url,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.update(INBOX_ID, MESSAGE_ID, UpdateEmailMessageParams(is_read=True))

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_update_should_return_updated_message(
        self, client: MessagesApi, sample_message_dict: dict
    ) -> None:
        url = f"{BASE_MESSAGES_URL}/{MESSAGE_ID}"
        updated_message_dict = sample_message_dict.copy()
        updated_message_dict["is_read"] = True

        responses.patch(
            url,
            json=updated_message_dict,
            status=200,
        )

        message = client.update(
            INBOX_ID, MESSAGE_ID, UpdateEmailMessageParams(is_read=True)
        )

        assert isinstance(message, EmailMessage)
        assert message.is_read is True

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
        client: MessagesApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        url = f"{BASE_MESSAGES_URL}/{MESSAGE_ID}"
        responses.delete(
            url,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.delete(INBOX_ID, MESSAGE_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_delete_should_return_deleted_message(
        self, client: MessagesApi, sample_message_dict: dict
    ) -> None:
        url = f"{BASE_MESSAGES_URL}/{MESSAGE_ID}"
        responses.delete(
            url,
            json=sample_message_dict,
            status=200,
        )

        result = client.delete(INBOX_ID, MESSAGE_ID)

        assert isinstance(result, EmailMessage)
        assert result.id == MESSAGE_ID

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
    def test_forward_should_raise_api_errors(
        self,
        client: MessagesApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        url = f"{BASE_MESSAGES_URL}/{MESSAGE_ID}/forward"
        responses.post(
            url,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.forward(INBOX_ID, MESSAGE_ID, "jack@mailtrap.io")

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_forward_should_return_forwarded_message(
        self, client: MessagesApi, sample_forwarded_message_dict: dict
    ) -> None:
        url = f"{BASE_MESSAGES_URL}/{MESSAGE_ID}/forward"
        responses.post(
            url,
            json=sample_forwarded_message_dict,
            status=200,
        )

        result = client.forward(INBOX_ID, MESSAGE_ID, "jack@mailtrap.io")

        assert result.message == "Your email message has been successfully forwarded"

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
    def test_get_spam_report_should_raise_api_errors(
        self,
        client: MessagesApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        url = f"{BASE_MESSAGES_URL}/{MESSAGE_ID}/spam_report"
        responses.get(
            url,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.get_spam_report(INBOX_ID, MESSAGE_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_spam_report_should_return_spam_report(
        self, client: MessagesApi, sample_spam_report_dict: dict
    ) -> None:
        url = f"{BASE_MESSAGES_URL}/{MESSAGE_ID}/spam_report"
        responses.get(
            url,
            json=sample_spam_report_dict,
            status=200,
        )

        result = client.get_spam_report(INBOX_ID, MESSAGE_ID)

        assert result.response_code == 2
        assert result.spam is False
        assert result.score == 1.2

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
    def test_get_html_analysis_should_raise_api_errors(
        self,
        client: MessagesApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        url = f"{BASE_MESSAGES_URL}/{MESSAGE_ID}/analyze"
        responses.get(
            url,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.get_html_analysis(INBOX_ID, MESSAGE_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_html_analysis_should_return_analysis_report(
        self, client: MessagesApi, sample_html_analysis_dict: dict
    ) -> None:
        url = f"{BASE_MESSAGES_URL}/{MESSAGE_ID}/analyze"
        responses.get(
            url,
            json=sample_html_analysis_dict,
            status=200,
        )

        result = client.get_html_analysis(INBOX_ID, MESSAGE_ID)

        assert result.status == "success"
        assert len(result.errors) == 1
        assert result.errors[0].error_line == 15

    @pytest.mark.parametrize(
        "status_code,response_body,expected_error_message,content_type",
        [
            (
                conftest.UNAUTHORIZED_STATUS_CODE,
                '{"error": "Incorrect API token"}',
                conftest.UNAUTHORIZED_ERROR_MESSAGE,
                "text/plain",
            ),
            (
                conftest.FORBIDDEN_STATUS_CODE,
                '{"errors": "Inbox is not active or you have insufficient permissions"}',
                "Inbox is not active or you have insufficient permissions",
                "text/plain",
            ),
            (
                conftest.NOT_FOUND_STATUS_CODE,
                "",
                conftest.NOT_FOUND_ERROR_MESSAGE,
                "text/plain",
            ),
        ],
    )
    @responses.activate
    def test_get_text_message_should_raise_api_errors(
        self,
        client: MessagesApi,
        status_code: int,
        response_body: str,
        expected_error_message: str,
        content_type: str,
    ) -> None:
        url = f"{BASE_MESSAGES_URL}/{MESSAGE_ID}/body.txt"
        responses.get(
            url,
            status=status_code,
            body=response_body,
            content_type=content_type,
        )

        with pytest.raises(APIError) as exc_info:
            client.get_text_message(INBOX_ID, MESSAGE_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_text_message_should_return_text_content(
        self, client: MessagesApi
    ) -> None:
        url = f"{BASE_MESSAGES_URL}/{MESSAGE_ID}/body.txt"
        text_content = "Congrats for sending test email with Mailtrap!"
        responses.get(
            url,
            body=text_content,
            status=200,
            content_type="text/plain",
        )

        result = client.get_text_message(INBOX_ID, MESSAGE_ID)

        assert result == text_content

    @pytest.mark.parametrize(
        "status_code,response_body,expected_error_message,content_type",
        [
            (
                conftest.UNAUTHORIZED_STATUS_CODE,
                '{"error": "Incorrect API token"}',
                conftest.UNAUTHORIZED_ERROR_MESSAGE,
                "application/json",
            ),
            (
                conftest.FORBIDDEN_STATUS_CODE,
                '{"errors": "Inbox is not active or you have insufficient permissions"}',
                "Inbox is not active or you have insufficient permissions",
                "application/json",
            ),
            (
                conftest.NOT_FOUND_STATUS_CODE,
                "",
                conftest.NOT_FOUND_ERROR_MESSAGE,
                "text/html",
            ),
        ],
    )
    @responses.activate
    def test_get_html_message_should_raise_api_errors(
        self,
        client: MessagesApi,
        status_code: int,
        response_body: str,
        expected_error_message: str,
        content_type: str,
    ) -> None:
        url = f"{BASE_MESSAGES_URL}/{MESSAGE_ID}/body.html"
        responses.get(
            url,
            status=status_code,
            body=response_body,
            content_type=content_type,
        )

        with pytest.raises(APIError) as exc_info:
            client.get_html_message(INBOX_ID, MESSAGE_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_html_message_should_return_html_content(
        self, client: MessagesApi
    ) -> None:
        url = f"{BASE_MESSAGES_URL}/{MESSAGE_ID}/body.html"
        html_content = "<html><body>Test HTML content</body></html>"
        responses.get(
            url,
            body=html_content,
            status=200,
            content_type="text/html",
        )

        result = client.get_html_message(INBOX_ID, MESSAGE_ID)

        assert result == html_content

    @pytest.mark.parametrize(
        "status_code,response_body,expected_error_message,content_type",
        [
            (
                conftest.UNAUTHORIZED_STATUS_CODE,
                '{"error": "Incorrect API token"}',
                conftest.UNAUTHORIZED_ERROR_MESSAGE,
                "text/plain",
            ),
            (
                conftest.FORBIDDEN_STATUS_CODE,
                '{"errors": "Inbox is not active or you have insufficient permissions"}',
                "Inbox is not active or you have insufficient permissions",
                "text/plain",
            ),
            (
                conftest.NOT_FOUND_STATUS_CODE,
                "",
                conftest.NOT_FOUND_ERROR_MESSAGE,
                "text/plain",
            ),
        ],
    )
    @responses.activate
    def test_get_raw_message_should_raise_api_errors(
        self,
        client: MessagesApi,
        status_code: int,
        response_body: str,
        expected_error_message: str,
        content_type: str,
    ) -> None:
        url = f"{BASE_MESSAGES_URL}/{MESSAGE_ID}/body.raw"
        responses.get(
            url,
            status=status_code,
            body=response_body,
            content_type=content_type,
        )

        with pytest.raises(APIError) as exc_info:
            client.get_raw_message(INBOX_ID, MESSAGE_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_raw_message_should_return_raw_content(self, client: MessagesApi) -> None:
        url = f"{BASE_MESSAGES_URL}/{MESSAGE_ID}/body.raw"
        raw_content = (
            "From: test@example.com\nTo: recipient@example.com\n"
            "Subject: Test\n\nBody content"
        )
        responses.get(
            url,
            body=raw_content,
            status=200,
            content_type="text/plain",
        )

        result = client.get_raw_message(INBOX_ID, MESSAGE_ID)

        assert result == raw_content

    @pytest.mark.parametrize(
        "status_code,response_body,expected_error_message,content_type",
        [
            (
                conftest.UNAUTHORIZED_STATUS_CODE,
                '{"error": "Incorrect API token"}',
                conftest.UNAUTHORIZED_ERROR_MESSAGE,
                "text/plain",
            ),
            (
                conftest.FORBIDDEN_STATUS_CODE,
                '{"errors": "Inbox is not active or you have insufficient permissions"}',
                "Inbox is not active or you have insufficient permissions",
                "text/plain",
            ),
            (
                conftest.NOT_FOUND_STATUS_CODE,
                "",
                conftest.NOT_FOUND_ERROR_MESSAGE,
                "text/html",
            ),
        ],
    )
    @responses.activate
    def test_get_html_source_should_raise_api_errors(
        self,
        client: MessagesApi,
        status_code: int,
        response_body: str,
        expected_error_message: str,
        content_type: str,
    ) -> None:
        url = f"{BASE_MESSAGES_URL}/{MESSAGE_ID}/body.htmlsource"
        responses.get(
            url,
            status=status_code,
            body=response_body,
            content_type=content_type,
        )

        with pytest.raises(APIError) as exc_info:
            client.get_html_source(INBOX_ID, MESSAGE_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_html_source_should_return_html_source(self, client: MessagesApi) -> None:
        url = f"{BASE_MESSAGES_URL}/{MESSAGE_ID}/body.htmlsource"
        html_source = "<!doctype html><html><head></head><body>Source</body></html>"
        responses.get(
            url,
            body=html_source,
            status=200,
            content_type="text/html",
        )

        result = client.get_html_source(INBOX_ID, MESSAGE_ID)

        assert result == html_source

    @pytest.mark.parametrize(
        "status_code,response_body,expected_error_message,content_type",
        [
            (
                conftest.UNAUTHORIZED_STATUS_CODE,
                '{"error": "Incorrect API token"}',
                conftest.UNAUTHORIZED_ERROR_MESSAGE,
                "text/plain",
            ),
            (
                conftest.FORBIDDEN_STATUS_CODE,
                '{"errors": "Inbox is not active or you have insufficient permissions"}',
                "Inbox is not active or you have insufficient permissions",
                "text/plain",
            ),
            (
                conftest.NOT_FOUND_STATUS_CODE,
                "",
                conftest.NOT_FOUND_ERROR_MESSAGE,
                "text/plain",
            ),
        ],
    )
    @responses.activate
    def test_get_message_as_eml_should_raise_api_errors(
        self,
        client: MessagesApi,
        status_code: int,
        response_body: str,
        expected_error_message: str,
        content_type: str,
    ) -> None:
        url = f"{BASE_MESSAGES_URL}/{MESSAGE_ID}/body.eml"
        responses.get(
            url,
            status=status_code,
            body=response_body,
            content_type=content_type,
        )

        with pytest.raises(APIError) as exc_info:
            client.get_message_as_eml(INBOX_ID, MESSAGE_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_message_as_eml_should_return_eml_content(
        self, client: MessagesApi
    ) -> None:
        url = f"{BASE_MESSAGES_URL}/{MESSAGE_ID}/body.eml"
        eml_content = (
            "From: test@example.com\nTo: recipient@example.com\n"
            "Subject: Test\n\nBody content"
        )
        responses.get(
            url,
            body=eml_content,
            status=200,
            content_type="message/rfc822",
        )

        result = client.get_message_as_eml(INBOX_ID, MESSAGE_ID)

        assert result == eml_content

    @responses.activate
    def test_get_mail_headers_should_return_headers(
        self, client: MessagesApi, sample_mail_headers_dict: dict
    ) -> None:
        url = f"{BASE_MESSAGES_URL}/{MESSAGE_ID}/mail_headers"
        responses.get(
            url,
            json=sample_mail_headers_dict,
            status=200,
        )

        result = client.get_mail_headers(INBOX_ID, MESSAGE_ID)

        assert result == sample_mail_headers_dict["headers"]
