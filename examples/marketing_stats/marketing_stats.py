import os
from datetime import date
from datetime import timedelta
from typing import Optional

import mailtrap as mt
from mailtrap.models.marketing_stats import MarketingStats

API_KEY = os.environ["MAILTRAP_API_KEY"]

client = mt.MailtrapClient(token=API_KEY)
marketing_stats_api = client.marketing_stats_api.marketing_stats


def last_30_days() -> tuple[str, str]:
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    return start_date.isoformat(), end_date.isoformat()


def get_marketing_stats() -> MarketingStats:
    # Campaigns and automations together, across every sending domain and
    # email service provider of the account.
    start_date, end_date = last_30_days()
    return marketing_stats_api.get(
        params=mt.MarketingStatsFilterParams(start_date=start_date, end_date=end_date)
    )


def get_marketing_stats_with_filters(
    sending_domain_ids: Optional[list[int]] = None,
) -> MarketingStats:
    # Campaigns only (pass ["automations"] for automations), for recipients at
    # Google and Yahoo. `sending_domain_ids` takes IDs from the Sending Domains
    # API; None includes every sending domain of the account.
    start_date, end_date = last_30_days()
    return marketing_stats_api.get(
        params=mt.MarketingStatsFilterParams(
            start_date=start_date,
            end_date=end_date,
            sending_domain_ids=sending_domain_ids,
            sources=["campaigns"],
            email_service_providers=["Google", "Yahoo"],
        )
    )


if __name__ == "__main__":
    print(get_marketing_stats())
    print(get_marketing_stats_with_filters())
