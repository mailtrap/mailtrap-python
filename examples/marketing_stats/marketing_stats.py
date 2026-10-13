import os
from datetime import datetime
from datetime import timedelta
from datetime import timezone

import mailtrap as mt
from mailtrap.models.marketing_stats import MarketingStats

API_KEY = os.environ["MAILTRAP_API_KEY"]

client = mt.MailtrapClient(token=API_KEY)
marketing_stats_api = client.marketing_stats_api.marketing_stats


def last_30_days() -> tuple[str, str]:
    # Both dates are inclusive, so today plus the 29 days before it is 30 days.
    end_date = datetime.now(timezone.utc).date()
    start_date = end_date - timedelta(days=29)
    return start_date.isoformat(), end_date.isoformat()


def get_marketing_stats() -> MarketingStats:
    # Campaigns and automations together, across every sending domain and
    # email service provider of the account.
    start_date, end_date = last_30_days()
    return marketing_stats_api.get(
        params=mt.MarketingStatsFilterParams(start_date=start_date, end_date=end_date)
    )


def get_marketing_stats_with_filters() -> MarketingStats:
    # Campaigns only (pass ["automations"] for automations), for two sending
    # domains (IDs from the Sending Domains API) and recipients at Google and
    # Yahoo.
    start_date, end_date = last_30_days()
    return marketing_stats_api.get(
        params=mt.MarketingStatsFilterParams(
            start_date=start_date,
            end_date=end_date,
            sending_domain_ids=[1, 2],
            sources=["campaigns"],
            email_service_providers=["Google", "Yahoo"],
        )
    )


if __name__ == "__main__":
    print(get_marketing_stats())
    print(get_marketing_stats_with_filters())
