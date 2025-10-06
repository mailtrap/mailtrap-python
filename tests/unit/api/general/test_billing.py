from typing import Any

import pytest
import responses

from mailtrap.api.resources.billing import BillingApi
from mailtrap.config import GENERAL_HOST
from mailtrap.exceptions import APIError
from mailtrap.http import HttpClient
from mailtrap.models.billing import BillingCycleUsage
from tests import conftest

ACCOUNT_ID = 26730
BASE_BILLING_URL = f"https://{GENERAL_HOST}/api/accounts/{ACCOUNT_ID}/billing/usage"


@pytest.fixture
def client() -> BillingApi:
    return BillingApi(client=HttpClient(GENERAL_HOST))


@pytest.fixture
def sample_billing_usage_dict() -> dict[str, Any]:
    return {
        "billing": {
            "cycle_start": "2023-01-01T00:00:00Z",
            "cycle_end": "2023-01-31T23:59:59Z",
        },
        "testing": {
            "plan": {"name": "Free"},
            "usage": {
                "sent_messages_count": {"current": 100, "limit": 1000},
                "forwarded_messages_count": {"current": 5, "limit": 100},
            },
        },
        "sending": {
            "plan": {"name": "Free"},
            "usage": {"sent_messages_count": {"current": 50, "limit": 500}},
        },
    }


class TestBillingApi:

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
    def test_get_current_billing_usage_should_raise_api_errors(
        self,
        client: BillingApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.get(
            BASE_BILLING_URL,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.get_current_billing_usage(ACCOUNT_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_current_billing_usage_should_return_billing_usage(
        self, client: BillingApi, sample_billing_usage_dict: dict
    ) -> None:
        responses.get(
            BASE_BILLING_URL,
            json=sample_billing_usage_dict,
            status=200,
        )

        billing_usage = client.get_current_billing_usage(ACCOUNT_ID)

        assert isinstance(billing_usage, BillingCycleUsage)
        assert billing_usage.testing.plan.name == "Free"
        assert billing_usage.testing.usage.sent_messages_count.current == 100
        assert billing_usage.testing.usage.sent_messages_count.limit == 1000
        assert billing_usage.testing.usage.forwarded_messages_count.current == 5
        assert billing_usage.testing.usage.forwarded_messages_count.limit == 100
        assert billing_usage.sending.plan.name == "Free"
        assert billing_usage.sending.usage.sent_messages_count.current == 50
        assert billing_usage.sending.usage.sent_messages_count.limit == 500
