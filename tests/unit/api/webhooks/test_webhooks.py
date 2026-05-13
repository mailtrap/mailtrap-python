from typing import Any

import pytest
import responses

from mailtrap.api.resources.webhooks import WebhooksApi
from mailtrap.config import GENERAL_HOST
from mailtrap.exceptions import APIError
from mailtrap.http import HttpClient
from mailtrap.models.common import DeletedObject
from mailtrap.models.webhooks import CreateWebhookParams
from mailtrap.models.webhooks import UpdateWebhookParams
from mailtrap.models.webhooks import Webhook
from mailtrap.models.webhooks import WebhookWithSecret
from tests import conftest

ACCOUNT_ID = "26730"
WEBHOOK_ID = 1
BASE_WEBHOOKS_URL = f"https://{GENERAL_HOST}/api/accounts/{ACCOUNT_ID}/webhooks"


@pytest.fixture
def client() -> WebhooksApi:
    return WebhooksApi(client=HttpClient(GENERAL_HOST), account_id=ACCOUNT_ID)


@pytest.fixture
def sample_webhook_dict() -> dict[str, Any]:
    return {
        "id": WEBHOOK_ID,
        "url": "https://example.com/mailtrap/webhooks",
        "active": True,
        "webhook_type": "email_sending",
        "payload_format": "json",
        "sending_stream": "transactional",
        "domain_id": 435,
        "event_types": ["delivery", "bounce"],
    }


class TestWebhooksApi:

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
        client: WebhooksApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.get(BASE_WEBHOOKS_URL, status=status_code, json=response_json)

        with pytest.raises(APIError) as exc_info:
            client.get_list()

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_list_should_return_webhooks_list(
        self, client: WebhooksApi, sample_webhook_dict: dict
    ) -> None:
        responses.get(
            BASE_WEBHOOKS_URL,
            json={
                "data": [
                    sample_webhook_dict,
                    {
                        "id": 2,
                        "url": "https://example.com/mailtrap/webhooks",
                        "active": True,
                        "webhook_type": "audit_log",
                        "payload_format": "json",
                    },
                ]
            },
            status=200,
        )

        webhooks = client.get_list()

        assert isinstance(webhooks, list)
        assert all(isinstance(w, Webhook) for w in webhooks)
        assert len(webhooks) == 2
        assert webhooks[0].id == WEBHOOK_ID
        assert webhooks[0].sending_stream == "transactional"
        assert webhooks[0].domain_id == 435
        assert webhooks[0].event_types == ["delivery", "bounce"]
        # audit_log webhook has no sending_stream / domain_id / event_types
        assert webhooks[1].webhook_type == "audit_log"
        assert webhooks[1].sending_stream is None
        assert webhooks[1].domain_id is None
        assert webhooks[1].event_types == []

    @responses.activate
    def test_get_list_should_return_empty_list(self, client: WebhooksApi) -> None:
        responses.get(BASE_WEBHOOKS_URL, json={"data": []}, status=200)

        webhooks = client.get_list()

        assert webhooks == []

    @responses.activate
    def test_get_list_should_silently_drop_extra_response_fields(
        self, client: WebhooksApi, sample_webhook_dict: dict
    ) -> None:
        responses.get(
            BASE_WEBHOOKS_URL,
            json={
                "data": [
                    {
                        **sample_webhook_dict,
                        "domain_name": "example.com",
                        "permissions": {"can_read": True, "can_update": True},
                    }
                ]
            },
            status=200,
        )

        webhooks = client.get_list()

        assert len(webhooks) == 1
        assert webhooks[0].id == WEBHOOK_ID

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
    def test_get_by_id_should_raise_api_errors(
        self,
        client: WebhooksApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.get(
            f"{BASE_WEBHOOKS_URL}/{WEBHOOK_ID}",
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.get_by_id(WEBHOOK_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_by_id_should_return_webhook(
        self, client: WebhooksApi, sample_webhook_dict: dict
    ) -> None:
        responses.get(
            f"{BASE_WEBHOOKS_URL}/{WEBHOOK_ID}",
            json={"data": sample_webhook_dict},
            status=200,
        )

        webhook = client.get_by_id(WEBHOOK_ID)

        assert isinstance(webhook, Webhook)
        assert webhook.id == WEBHOOK_ID
        assert webhook.url == "https://example.com/mailtrap/webhooks"

    @pytest.mark.parametrize(
        "status_code,response_json,expected_error_message",
        [
            (
                conftest.UNAUTHORIZED_STATUS_CODE,
                conftest.UNAUTHORIZED_RESPONSE,
                conftest.UNAUTHORIZED_ERROR_MESSAGE,
            ),
            (
                conftest.VALIDATION_ERRORS_STATUS_CODE,
                {"errors": "Url is invalid"},
                "Url is invalid",
            ),
        ],
    )
    @responses.activate
    def test_create_should_raise_api_errors(
        self,
        client: WebhooksApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.post(BASE_WEBHOOKS_URL, status=status_code, json=response_json)

        with pytest.raises(APIError) as exc_info:
            client.create(
                CreateWebhookParams(
                    url="https://example.com/mailtrap/webhooks",
                    webhook_type="email_sending",
                )
            )

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_create_should_return_webhook_with_signing_secret(
        self, client: WebhooksApi, sample_webhook_dict: dict
    ) -> None:
        responses.post(
            BASE_WEBHOOKS_URL,
            json={"data": {**sample_webhook_dict, "signing_secret": "a1b2c3d4"}},
            status=200,
        )

        webhook = client.create(
            CreateWebhookParams(
                url="https://example.com/mailtrap/webhooks",
                webhook_type="email_sending",
                sending_stream="transactional",
                event_types=["delivery", "bounce"],
                domain_id=435,
            )
        )

        assert isinstance(webhook, WebhookWithSecret)
        assert webhook.id == WEBHOOK_ID
        assert webhook.signing_secret == "a1b2c3d4"

        assert len(responses.calls) == 1
        assert responses.calls[0].request.body == (
            b'{"webhook": {"url": "https://example.com/mailtrap/webhooks", '
            b'"webhook_type": "email_sending", "sending_stream": "transactional", '
            b'"event_types": ["delivery", "bounce"], "domain_id": 435}}'
        )

    @responses.activate
    def test_update_should_send_only_supplied_fields(
        self, client: WebhooksApi, sample_webhook_dict: dict
    ) -> None:
        responses.patch(
            f"{BASE_WEBHOOKS_URL}/{WEBHOOK_ID}",
            json={"data": {**sample_webhook_dict, "active": False}},
            status=200,
        )

        webhook = client.update(WEBHOOK_ID, UpdateWebhookParams(active=False))

        assert isinstance(webhook, Webhook)
        assert webhook.active is False

        assert responses.calls[0].request.body == b'{"webhook": {"active": false}}'

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
    def test_update_should_raise_api_errors(
        self,
        client: WebhooksApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.patch(
            f"{BASE_WEBHOOKS_URL}/{WEBHOOK_ID}",
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.update(WEBHOOK_ID, UpdateWebhookParams(active=False))

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
    def test_delete_should_raise_api_errors(
        self,
        client: WebhooksApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.delete(
            f"{BASE_WEBHOOKS_URL}/{WEBHOOK_ID}",
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.delete(WEBHOOK_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_delete_should_return_deleted_object(
        self, client: WebhooksApi, sample_webhook_dict: dict
    ) -> None:
        responses.delete(
            f"{BASE_WEBHOOKS_URL}/{WEBHOOK_ID}",
            json={"data": sample_webhook_dict},
            status=200,
        )

        result = client.delete(WEBHOOK_ID)

        assert isinstance(result, DeletedObject)
        assert result.id == WEBHOOK_ID
