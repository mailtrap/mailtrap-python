from typing import Literal
from typing import Optional

from pydantic.dataclasses import dataclass

from mailtrap.models.common import RequestParams

MarketingStatsSource = Literal["campaigns", "automations"]


@dataclass
class MarketingStats:
    """
    Aggregated Email Marketing metrics (campaigns and automations). Rates are
    fractions from 0 to 1: delivery and bounce rates are shares of
    ``sent_count``, the rest are shares of ``delivery_count``. Every count and
    rate is ``0`` when nothing matched the filters.
    """

    delivery_count: int
    delivery_rate: float
    bounce_count: int
    bounce_rate: float
    open_count: int
    open_rate: float
    click_count: int
    click_rate: float
    spam_count: int
    spam_rate: float
    unsubscription_count: int
    unsubscription_rate: float
    sent_count: int


@dataclass
class MarketingStatsResponse:
    """Envelope of the marketing stats response."""

    data: MarketingStats


@dataclass
class MarketingStatsFilterParams(RequestParams):
    """
    Query params for marketing stats. ``start_date`` and ``end_date`` are
    required and inclusive (``YYYY-MM-DD``). Omitted list filters include
    everything; one source narrows the results to campaigns or automations.
    """

    start_date: str
    end_date: str
    sending_domain_ids: Optional[list[int]] = None
    sources: Optional[list[MarketingStatsSource]] = None
    email_service_providers: Optional[list[str]] = None
