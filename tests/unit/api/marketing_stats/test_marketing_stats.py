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


SAMPLE_STATS: dict[str, Any] = {
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

    @pytest.mark.parametrize(
        "stats_dict",
        [SAMPLE_STATS, dict.fromkeys(SAMPLE_STATS, 0)],
        ids=["with_activity", "nothing_matched"],
    )
    @responses.activate
    def test_get_should_unwrap_data_envelope(
        self, client: MarketingStatsApi, stats_dict: dict[str, Any]
    ) -> None:
        responses.get(
            MARKETING_STATS_URL,
            json={"data": stats_dict},
            status=200,
        )

        stats = client.get(_default_params())

        assert stats == MarketingStats(**stats_dict)

    @pytest.mark.parametrize(
        "params,expected_query",
        [
            (
                _default_params(),
                {"start_date": ["2026-05-01"], "end_date": ["2026-05-31"]},
            ),
            (
                MarketingStatsFilterParams(
                    start_date="2026-05-01",
                    end_date="2026-05-31",
                    sending_domain_ids=[3938, 3939],
                    sources=["campaigns"],
                    email_service_providers=["Google", "Google Workspace"],
                ),
                {
                    "start_date": ["2026-05-01"],
                    "end_date": ["2026-05-31"],
                    "sending_domain_ids[]": ["3938", "3939"],
                    "sources[]": ["campaigns"],
                    "email_service_providers[]": ["Google", "Google Workspace"],
                },
            ),
        ],
        ids=["dates_only", "with_filters_as_array_params"],
    )
    @responses.activate
    def test_get_should_send_query_params(
        self,
        client: MarketingStatsApi,
        params: MarketingStatsFilterParams,
        expected_query: dict[str, list[str]],
    ) -> None:
        responses.get(
            MARKETING_STATS_URL,
            json={"data": SAMPLE_STATS},
            status=200,
        )

        client.get(params)

        query = parse_qs(urlparse(responses.calls[0].request.url).query)
        assert query == expected_query


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
