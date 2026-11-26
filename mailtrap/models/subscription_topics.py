"""Models for the Subscription Topics API (``/api/subscription_topics``)."""

from typing import Optional

from pydantic import Field
from pydantic.dataclasses import dataclass

from mailtrap.models.common import Pagination
from mailtrap.models.common import RequestParams


@dataclass
class SubscriptionTopic:
    """
    A subscription topic contacts can unsubscribe from on its own.
    ``domain_id`` is the sending domain the topic covers, or ``None`` when it
    covers every domain. ``deleted_at`` is set only on a deleted topic, which
    the list leaves out but ``get_by_id`` still returns.
    """

    id: int
    name: str
    created_at: str
    updated_at: str
    description: Optional[str] = None
    domain_id: Optional[int] = None
    deleted_at: Optional[str] = None


@dataclass
class SubscriptionTopicResponse:
    """Envelope of a single-topic response."""

    data: SubscriptionTopic


@dataclass
class SubscriptionTopicListResponse:
    """Paginated response from listing subscription topics."""

    data: list[SubscriptionTopic] = Field(default_factory=list)
    pagination: Optional[Pagination] = None


@dataclass
class SubscriptionTopicListParams(RequestParams):
    """
    Query params for listing subscription topics. ``token`` is the page number
    and ``per_page`` is capped at 100 (default 50).
    """

    per_page: Optional[int] = None
    token: Optional[int] = None
