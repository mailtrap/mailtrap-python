from mailtrap.api.resources.marketing_stats import MarketingStatsApi
from mailtrap.http import HttpClient


class MarketingStatsBaseApi:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    @property
    def marketing_stats(self) -> MarketingStatsApi:
        return MarketingStatsApi(client=self._client)
