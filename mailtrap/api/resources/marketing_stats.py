from mailtrap.http import HttpClient
from mailtrap.models.marketing_stats import MarketingStats
from mailtrap.models.marketing_stats import MarketingStatsFilterParams
from mailtrap.models.marketing_stats import MarketingStatsResponse


class MarketingStatsApi:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def get(self, params: MarketingStatsFilterParams) -> MarketingStats:
        """
        Get aggregated Email Marketing stats, campaigns and automations
        together, for a date range. Email API/SMTP traffic is not included;
        ``stats_api`` reports it.
        """
        response = self._client.get(
            "/api/marketing/stats", params=params.api_query_params
        )
        return MarketingStatsResponse(**response).data
