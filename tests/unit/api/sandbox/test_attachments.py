from typing import Any

import pytest
import responses

from mailtrap.api.resources.attachments import AttachmentsApi
from mailtrap.config import GENERAL_HOST
from mailtrap.exceptions import APIError
from mailtrap.http import HttpClient
from mailtrap.models.attachments import Attachment
from tests import conftest

ACCOUNT_ID = "321"
INBOX_ID = 123
MESSAGE_ID = 457
ATTACHMENT_ID = 67

BASE_ATTACHMENTS_URL = (
    f"https://{GENERAL_HOST}/api/accounts/{ACCOUNT_ID}"
    f"/inboxes/{INBOX_ID}"
    f"/messages/{MESSAGE_ID}"
    "/attachments"
)


@pytest.fixture
def client() -> AttachmentsApi:
    return AttachmentsApi(account_id=ACCOUNT_ID, client=HttpClient(GENERAL_HOST))


@pytest.fixture
def sample_attachment_dict() -> dict[str, Any]:
    return {
        "id": ATTACHMENT_ID,
        "message_id": 457,
        "filename": "test.csv",
        "attachment_type": "inline",
        "content_type": "plain/text",
        "content_id": None,
        "transfer_encoding": None,
        "attachment_size": 0,
        "created_at": "2022-06-02T19:25:54.827Z",
        "updated_at": "2022-06-02T19:25:54.827Z",
        "attachment_human_size": "0 Bytes",
        "download_path": (
            "/api/accounts/321"
            "/inboxes/123"
            "/messages/457"
            f"/attachments/{ATTACHMENT_ID}/download"
        ),
    }


class TestProjectsApi:
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
        client: AttachmentsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.get(
            BASE_ATTACHMENTS_URL,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.get_list(INBOX_ID, MESSAGE_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_list_should_return_attachments_list(
        self, client: AttachmentsApi, sample_attachment_dict: dict
    ) -> None:
        responses.get(
            BASE_ATTACHMENTS_URL,
            json=[sample_attachment_dict],
            status=200,
        )

        attachments = client.get_list(INBOX_ID, MESSAGE_ID)

        assert isinstance(attachments, list)
        assert all(isinstance(a, Attachment) for a in attachments)
        assert attachments[0].id == ATTACHMENT_ID

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
    def test_get_should_raise_api_errors(
        self,
        client: AttachmentsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        url = f"{BASE_ATTACHMENTS_URL}/{ATTACHMENT_ID}"
        responses.get(
            url,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.get(INBOX_ID, MESSAGE_ID, ATTACHMENT_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_should_return_single_attachment(
        self, client: AttachmentsApi, sample_attachment_dict: dict
    ) -> None:
        url = f"{BASE_ATTACHMENTS_URL}/{ATTACHMENT_ID}"
        responses.get(
            url,
            json=sample_attachment_dict,
            status=200,
        )

        attachment = client.get(INBOX_ID, MESSAGE_ID, ATTACHMENT_ID)

        assert isinstance(attachment, Attachment)
        assert attachment.id == ATTACHMENT_ID
