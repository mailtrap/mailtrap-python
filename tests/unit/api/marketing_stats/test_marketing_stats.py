from typing import Any
from urllib.parse import parse_qs
from urllib.parse import urlparse

import pytest
import responses
from pydantic import ValidationError

from mailtrap.api.resources.marketing_stats import MarketingStatsApi
from mailtrap.config import GENERAL_HOST
from mailtrap.exceptions import APIError
from mailtrap.http import HttpClient
from mailtrap.models.marketing_stats import MarketingStats
from mailtrap.models.marketing_stats import MarketingStatsFilterParams
from tests import conftest

MARKETING_STATS_URL = f"https://{GENERAL_HOST}/api/marketing/stats"


@pytest.fixture
def client() -> MarketingStatsApi:
    return MarketingStatsApi(client=HttpClient(GENERAL_HOST))


@pytest.fixture
def sample_stats_dict() -> dict[str, Any]:
    return {
        "delivery_count": 1200,
        "delivery_rate": 0.96,
        "bounce_count": 50,
        "bounce_rate": 0.04,
        "open_count": 600,
        "open_rate": 0.5,
        "click_count": 240,
        "click_rate": 0.2,
        "spam_count": 3,
        "spam_rate": 0.0025,
        "unsubscription_count": 12,
        "unsubscription_rate": 0.01,
        "sent_count": 1250,
    }


def _default_params() -> MarketingStatsFilterParams:
    return MarketingStatsFilterParams(start_date="2026-05-01", end_date="2026-05-31")


class TestMarketingStatsApi:

    @pytest.mark.parametrize(
        "status_code,response_json,expected_error_message",
        [
            (
                400,
                {"errors": "Invalid end_date: '2026-13-01'"},
                "Invalid end_date: '2026-13-01'",
            ),
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
        ],
    )
    @responses.activate
    def test_get_should_raise_api_errors(
        self,
        client: MarketingStatsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.get(
            MARKETING_STATS_URL,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.get(_default_params())

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_should_unwrap_data_envelope(
        self, client: MarketingStatsApi, sample_stats_dict: dict
    ) -> None:
        responses.get(
            MARKETING_STATS_URL,
            json={"data": sample_stats_dict},
            status=200,
        )

        stats = client.get(_default_params())

        assert isinstance(stats, MarketingStats)
        assert stats.delivery_count == 1200
        assert stats.delivery_rate == 0.96
        assert stats.bounce_count == 50
        assert stats.bounce_rate == 0.04
        assert stats.open_count == 600
        assert stats.open_rate == 0.5
        assert stats.click_count == 240
        assert stats.click_rate == 0.2
        assert stats.spam_count == 3
        assert stats.spam_rate == 0.0025
        assert stats.unsubscription_count == 12
        assert stats.unsubscription_rate == 0.01
        assert stats.sent_count == 1250

    @responses.activate
    def test_get_should_send_only_dates_without_filters(
        self, client: MarketingStatsApi, sample_stats_dict: dict
    ) -> None:
        responses.get(
            MARKETING_STATS_URL,
            json={"data": sample_stats_dict},
            status=200,
        )

        client.get(_default_params())

        query = parse_qs(urlparse(responses.calls[0].request.url).query)
        assert query == {"start_date": ["2026-05-01"], "end_date": ["2026-05-31"]}

    @responses.activate
    def test_get_should_send_filters_as_array_query_params(
        self, client: MarketingStatsApi, sample_stats_dict: dict
    ) -> None:
        responses.get(
            MARKETING_STATS_URL,
            json={"data": sample_stats_dict},
            status=200,
        )

        client.get(
            MarketingStatsFilterParams(
                start_date="2026-05-01",
                end_date="2026-05-31",
                sending_domain_ids=[3938, 3939],
                sources=["campaigns"],
                email_service_providers=["Google", "Google Workspace"],
            )
        )

        query = parse_qs(urlparse(responses.calls[0].request.url).query)
        assert query == {
            "start_date": ["2026-05-01"],
            "end_date": ["2026-05-31"],
            "sending_domain_ids[]": ["3938", "3939"],
            "sources[]": ["campaigns"],
            "email_service_providers[]": ["Google", "Google Workspace"],
        }

    @responses.activate
    def test_get_should_return_zeros_when_nothing_matched(
        self, client: MarketingStatsApi
    ) -> None:
        zeros = {
            "delivery_count": 0,
            "delivery_rate": 0,
            "bounce_count": 0,
            "bounce_rate": 0,
            "open_count": 0,
            "open_rate": 0,
            "click_count": 0,
            "click_rate": 0,
            "spam_count": 0,
            "spam_rate": 0,
            "unsubscription_count": 0,
            "unsubscription_rate": 0,
            "sent_count": 0,
        }
        responses.get(
            MARKETING_STATS_URL,
            json={"data": zeros},
            status=200,
        )

        stats = client.get(_default_params())

        assert isinstance(stats, MarketingStats)
        assert stats.sent_count == 0
        assert stats.delivery_rate == 0.0
        assert stats.unsubscription_rate == 0.0


class TestMarketingStatsFilterParams:

    def test_should_reject_unknown_source(self) -> None:
        with pytest.raises(ValidationError):
            MarketingStatsFilterParams(
                start_date="2026-05-01",
                end_date="2026-05-31",
                sources=["newsletters"],  # type: ignore[list-item]
            )

    def test_should_require_both_dates(self) -> None:
        with pytest.raises(ValidationError):
            MarketingStatsFilterParams(start_date="2026-05-01")  # type: ignore[call-arg]
