from typing import Literal

from mailtrap.http import HttpClient
from mailtrap.models.stats import SendingStatGroup
from mailtrap.models.stats import SendingStats
from mailtrap.models.stats import StatsFilterParams

GroupKey = Literal["domains", "categories", "email_service_providers", "date"]

_GROUP_KEYS = {
    "domains": "sending_domain_id",
    "categories": "category",
    "email_service_providers": "email_service_provider",
    "date": "date",
}


class StatsApi:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def get(self, account_id: int, params: StatsFilterParams) -> SendingStats:
        """Get aggregated sending stats."""
        response = self._client.get(
            self._base_path(account_id),
            params=params.api_query_params,
        )
        return SendingStats(**response)

    def by_domain(
        self, account_id: int, params: StatsFilterParams
    ) -> list[SendingStatGroup]:
        """Get sending stats grouped by domains."""
        return self._grouped_stats(account_id, "domains", params)

    def by_category(
        self, account_id: int, params: StatsFilterParams
    ) -> list[SendingStatGroup]:
        """Get sending stats grouped by categories."""
        return self._grouped_stats(account_id, "categories", params)

    def by_email_service_provider(
        self, account_id: int, params: StatsFilterParams
    ) -> list[SendingStatGroup]:
        """Get sending stats grouped by email service providers."""
        return self._grouped_stats(account_id, "email_service_providers", params)

    def by_date(
        self, account_id: int, params: StatsFilterParams
    ) -> list[SendingStatGroup]:
        """Get sending stats grouped by date."""
        return self._grouped_stats(account_id, "date", params)

    def _grouped_stats(
        self, account_id: int, group: GroupKey, params: StatsFilterParams
    ) -> list[SendingStatGroup]:
        response = self._client.get(
            f"{self._base_path(account_id)}/{group}", params=params.api_query_params
        )
        group_key = _GROUP_KEYS[group]

        return [
            SendingStatGroup(
                name=group_key,
                value=item[group_key],
                stats=SendingStats(**item["stats"]),
            )
            for item in response
        ]

    @staticmethod
    def _base_path(account_id: int) -> str:
        return f"/api/accounts/{account_id}/stats"
