from typing import Any

import pytest
import responses

from mailtrap.api.resources.stats import StatsApi
from mailtrap.config import GENERAL_HOST
from mailtrap.exceptions import APIError
from mailtrap.http import HttpClient
from mailtrap.models.stats import SendingStatGroup
from mailtrap.models.stats import SendingStats
from mailtrap.models.stats import StatsFilterParams
from tests import conftest

ACCOUNT_ID = 26730
BASE_STATS_URL = f"https://{GENERAL_HOST}/api/accounts/{ACCOUNT_ID}/stats"


@pytest.fixture
def client() -> StatsApi:
    return StatsApi(client=HttpClient(GENERAL_HOST))


@pytest.fixture
def sample_stats_dict() -> dict[str, Any]:
    return {
        "delivery_count": 150,
        "delivery_rate": 0.95,
        "bounce_count": 8,
        "bounce_rate": 0.05,
        "open_count": 120,
        "open_rate": 0.8,
        "click_count": 60,
        "click_rate": 0.5,
        "spam_count": 2,
        "spam_rate": 0.013,
    }


@pytest.fixture
def sample_grouped_stats_response() -> list[dict[str, Any]]:
    return [
        {
            "sending_domain_id": 1,
            "stats": {
                "delivery_count": 100,
                "delivery_rate": 0.96,
                "bounce_count": 4,
                "bounce_rate": 0.04,
                "open_count": 80,
                "open_rate": 0.8,
                "click_count": 40,
                "click_rate": 0.5,
                "spam_count": 1,
                "spam_rate": 0.01,
            },
        },
        {
            "sending_domain_id": 2,
            "stats": {
                "delivery_count": 50,
                "delivery_rate": 0.93,
                "bounce_count": 4,
                "bounce_rate": 0.07,
                "open_count": 40,
                "open_rate": 0.8,
                "click_count": 20,
                "click_rate": 0.5,
                "spam_count": 1,
                "spam_rate": 0.02,
            },
        },
    ]


def _default_params() -> StatsFilterParams:
    return StatsFilterParams(start_date="2026-01-01", end_date="2026-01-31")


class TestStatsApi:

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
        client: StatsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.get(
            BASE_STATS_URL,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.get(ACCOUNT_ID, _default_params())

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_should_return_sending_stats(
        self, client: StatsApi, sample_stats_dict: dict
    ) -> None:
        responses.get(
            BASE_STATS_URL,
            json=sample_stats_dict,
            status=200,
        )

        stats = client.get(ACCOUNT_ID, _default_params())

        assert isinstance(stats, SendingStats)
        assert stats.delivery_count == 150
        assert stats.delivery_rate == 0.95
        assert stats.bounce_count == 8
        assert stats.bounce_rate == 0.05
        assert stats.open_count == 120
        assert stats.open_rate == 0.8
        assert stats.click_count == 60
        assert stats.click_rate == 0.5
        assert stats.spam_count == 2
        assert stats.spam_rate == 0.013

    @responses.activate
    def test_get_with_filter_params(
        self, client: StatsApi, sample_stats_dict: dict
    ) -> None:
        responses.get(
            BASE_STATS_URL,
            json=sample_stats_dict,
            status=200,
        )

        params = StatsFilterParams(
            start_date="2026-01-01",
            end_date="2026-01-31",
            sending_domain_ids=[1, 2],
            sending_streams=["transactional"],
            categories=["Welcome email"],
            email_service_providers=["Gmail"],
        )
        client.get(ACCOUNT_ID, params)

        request_params = responses.calls[0].request.params
        assert request_params["sending_domain_ids[]"] == ["1", "2"]
        assert request_params["sending_streams[]"] == "transactional"
        assert request_params["categories[]"] == "Welcome email"
        assert request_params["email_service_providers[]"] == "Gmail"

    @responses.activate
    def test_by_domain_should_return_grouped_stats(
        self, client: StatsApi, sample_grouped_stats_response: list
    ) -> None:
        responses.get(
            f"{BASE_STATS_URL}/domains",
            json=sample_grouped_stats_response,
            status=200,
        )

        result = client.by_domain(ACCOUNT_ID, _default_params())

        assert len(result) == 2
        assert isinstance(result[0], SendingStatGroup)
        assert result[0].name == "sending_domain_id"
        assert result[0].value == 1
        assert isinstance(result[0].stats, SendingStats)
        assert result[0].stats.delivery_count == 100
        assert result[1].name == "sending_domain_id"
        assert result[1].value == 2
        assert result[1].stats.delivery_count == 50

    @responses.activate
    def test_by_category_should_return_grouped_stats(self, client: StatsApi) -> None:
        response_data = [
            {
                "category": "Welcome email",
                "stats": {
                    "delivery_count": 100,
                    "delivery_rate": 0.97,
                    "bounce_count": 3,
                    "bounce_rate": 0.03,
                    "open_count": 85,
                    "open_rate": 0.85,
                    "click_count": 45,
                    "click_rate": 0.53,
                    "spam_count": 0,
                    "spam_rate": 0.0,
                },
            },
        ]
        responses.get(
            f"{BASE_STATS_URL}/categories",
            json=response_data,
            status=200,
        )

        result = client.by_category(ACCOUNT_ID, _default_params())

        assert len(result) == 1
        assert result[0].name == "category"
        assert result[0].value == "Welcome email"
        assert result[0].stats.delivery_count == 100

    @responses.activate
    def test_by_email_service_provider_should_return_grouped_stats(
        self, client: StatsApi
    ) -> None:
        response_data = [
            {
                "email_service_provider": "Gmail",
                "stats": {
                    "delivery_count": 80,
                    "delivery_rate": 0.97,
                    "bounce_count": 2,
                    "bounce_rate": 0.03,
                    "open_count": 70,
                    "open_rate": 0.88,
                    "click_count": 35,
                    "click_rate": 0.5,
                    "spam_count": 1,
                    "spam_rate": 0.013,
                },
            },
        ]
        responses.get(
            f"{BASE_STATS_URL}/email_service_providers",
            json=response_data,
            status=200,
        )

        result = client.by_email_service_provider(ACCOUNT_ID, _default_params())

        assert len(result) == 1
        assert result[0].name == "email_service_provider"
        assert result[0].value == "Gmail"
        assert result[0].stats.delivery_count == 80

    @responses.activate
    def test_by_date_should_return_grouped_stats(self, client: StatsApi) -> None:
        response_data = [
            {
                "date": "2026-01-01",
                "stats": {
                    "delivery_count": 5,
                    "delivery_rate": 1.0,
                    "bounce_count": 0,
                    "bounce_rate": 0.0,
                    "open_count": 4,
                    "open_rate": 0.8,
                    "click_count": 2,
                    "click_rate": 0.5,
                    "spam_count": 0,
                    "spam_rate": 0.0,
                },
            },
        ]
        responses.get(
            f"{BASE_STATS_URL}/date",
            json=response_data,
            status=200,
        )

        result = client.by_date(ACCOUNT_ID, _default_params())

        assert len(result) == 1
        assert result[0].name == "date"
        assert result[0].value == "2026-01-01"
        assert result[0].stats.delivery_count == 5
