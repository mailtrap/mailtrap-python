from typing import Optional
from typing import Union

from pydantic.dataclasses import dataclass

from mailtrap.models.common import RequestParams


@dataclass
class SendingStats:
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


@dataclass
class SendingStatGroup:
    name: str
    value: Union[str, int]
    stats: SendingStats


@dataclass
class StatsFilterParams(RequestParams):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    sending_domain_ids: Optional[list[int]] = None
    sending_streams: Optional[list[str]] = None
    categories: Optional[list[str]] = None
    email_service_providers: Optional[list[str]] = None
