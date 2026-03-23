import mailtrap as mt
from mailtrap.models.stats import SendingStatGroup
from mailtrap.models.stats import SendingStats
from mailtrap.models.stats import StatsFilterParams

API_TOKEN = "YOUR_API_TOKEN"
ACCOUNT_ID = "YOUR_ACCOUNT_ID"

client = mt.MailtrapClient(token=API_TOKEN)
stats_api = client.stats_api


def get_stats(account_id: int) -> SendingStats:
    params = StatsFilterParams(start_date="2026-01-01", end_date="2026-01-31")
    return stats_api.get(account_id=account_id, params=params)


def get_stats_by_domain(account_id: int) -> list[SendingStatGroup]:
    params = StatsFilterParams(start_date="2026-01-01", end_date="2026-01-31")
    return stats_api.by_domain(account_id=account_id, params=params)


def get_stats_by_category(account_id: int) -> list[SendingStatGroup]:
    params = StatsFilterParams(start_date="2026-01-01", end_date="2026-01-31")
    return stats_api.by_category(account_id=account_id, params=params)


def get_stats_by_email_service_provider(account_id: int) -> list[SendingStatGroup]:
    params = StatsFilterParams(start_date="2026-01-01", end_date="2026-01-31")
    return stats_api.by_email_service_provider(account_id=account_id, params=params)


def get_stats_by_date(account_id: int) -> list[SendingStatGroup]:
    params = StatsFilterParams(start_date="2026-01-01", end_date="2026-01-31")
    return stats_api.by_date(account_id=account_id, params=params)


def get_stats_with_filters(account_id: int) -> SendingStats:
    params = StatsFilterParams(
        start_date="2026-01-01",
        end_date="2026-01-31",
        sending_domain_ids=[1, 2],
        sending_streams=["transactional"],
        categories=["Welcome email", "Marketing"],
        email_service_providers=["Gmail", "Yahoo"],
    )
    return stats_api.get(account_id=account_id, params=params)


def get_stats_by_domain_with_filters(account_id: int) -> list[SendingStatGroup]:
    params = StatsFilterParams(
        start_date="2026-01-01",
        end_date="2026-01-31",
        sending_streams=["transactional"],
        categories=["Welcome email"],
    )
    return stats_api.by_domain(account_id=account_id, params=params)


if __name__ == "__main__":
    print(get_stats(ACCOUNT_ID))
    print(get_stats_by_domain(ACCOUNT_ID))
    print(get_stats_by_category(ACCOUNT_ID))
    print(get_stats_by_email_service_provider(ACCOUNT_ID))
    print(get_stats_by_date(ACCOUNT_ID))
    print(get_stats_with_filters(ACCOUNT_ID))
    print(get_stats_by_domain_with_filters(ACCOUNT_ID))
