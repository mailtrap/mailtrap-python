from datetime import datetime

from pydantic import Field
from pydantic.dataclasses import dataclass

from mailtrap.models.common import RequestParams


@dataclass
class TrackingOptOut:
    id: str
    email: str
    created_at: datetime
    domain_name: str | None = None


@dataclass
class TrackingOptOutResponse:
    data: TrackingOptOut


@dataclass
class TrackingOptOutsListResponse:
    """A page of tracking opt-outs. `last_id` is the cursor for the next page,
    or `None` when there are no more pages."""

    data: list[TrackingOptOut] = Field(default_factory=list)
    last_id: str | None = None


@dataclass
class TrackingOptOutsListParams(RequestParams):
    email: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    last_id: str | None = None


@dataclass
class CreateTrackingOptOutParams(RequestParams):
    email: str
    domain_id: int
