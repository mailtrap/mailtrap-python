"""Models for Email Logs API (list, get message, filters)."""

from typing import Any
from typing import Literal
from typing import Optional
from typing import Union

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic.dataclasses import dataclass

# --- Event details (for get-by-id) ---


@dataclass
class EventDetailsDelivery:
    sending_ip: Optional[str] = None
    recipient_mx: Optional[str] = None
    email_service_provider: Optional[str] = None


@dataclass
class EventDetailsOpen:
    web_ip_address: Optional[str] = None


@dataclass
class EventDetailsClick:
    click_url: Optional[str] = None
    web_ip_address: Optional[str] = None


@dataclass
class EventDetailsBounce:
    sending_ip: Optional[str] = None
    recipient_mx: Optional[str] = None
    email_service_provider: Optional[str] = None
    email_service_provider_status: Optional[str] = None
    email_service_provider_response: Optional[str] = None
    bounce_category: Optional[str] = None


@dataclass
class EventDetailsSpam:
    spam_feedback_type: Optional[str] = None


@dataclass
class EventDetailsUnsubscribe:
    web_ip_address: Optional[str] = None


@dataclass
class EventDetailsReject:
    reject_reason: Optional[str] = None


@dataclass
class MessageEvent:
    """Event attached to a message (delivery, open, click, bounce, etc.)."""

    event_type: str
    created_at: str
    details: Optional[
        Union[
            EventDetailsDelivery,
            EventDetailsOpen,
            EventDetailsClick,
            EventDetailsBounce,
            EventDetailsSpam,
            EventDetailsUnsubscribe,
            EventDetailsReject,
            dict[str, Any],
        ]
    ] = None


def _parse_event_details(
    event_type: str,
    data: Optional[dict[str, Any]],
) -> Optional[
    Union[
        EventDetailsDelivery,
        EventDetailsOpen,
        EventDetailsClick,
        EventDetailsBounce,
        EventDetailsSpam,
        EventDetailsUnsubscribe,
        EventDetailsReject,
        dict[str, Any],
    ]
]:
    """Build the correct EventDetails* from event_type and raw details dict."""
    if data is None:
        return None
    if event_type == "delivery":
        return EventDetailsDelivery(**data)
    if event_type == "open":
        return EventDetailsOpen(**data)
    if event_type == "click":
        return EventDetailsClick(**data)
    if event_type in ("soft_bounce", "bounce"):
        return EventDetailsBounce(**data)
    if event_type == "spam":
        return EventDetailsSpam(**data)
    if event_type == "unsubscribe":
        return EventDetailsUnsubscribe(**data)
    if event_type in ("suspension", "reject"):
        return EventDetailsReject(**data)
    return data


def _parse_message_event(event_dict: dict[str, Any]) -> MessageEvent:
    """Build MessageEvent from API dict using event_type to select details type."""
    event_type = event_dict["event_type"]
    created_at = event_dict["created_at"]
    details = _parse_event_details(event_type, event_dict.get("details"))
    return MessageEvent(
        event_type=event_type,
        created_at=created_at,
        details=details,
    )


class EmailLogMessage(BaseModel):
    """
    Email log message. Used for both list and get-by-id; from list response
    only summary fields are set, raw_message_url and events are empty.
    """

    model_config = ConfigDict(populate_by_name=True)

    message_id: str
    status: Literal["delivered", "not_delivered", "enqueued", "opted_out"]
    subject: Optional[str] = None
    from_: str = Field(alias="from")
    to: str
    sent_at: str
    client_ip: Optional[str] = None
    category: Optional[str] = None
    custom_variables: dict[str, Any] = Field(default_factory=dict)
    sending_stream: Literal["transactional", "bulk"]
    sending_domain_id: int
    template_id: Optional[int] = None
    template_variables: dict[str, Any] = Field(default_factory=dict)
    opens_count: int
    clicks_count: int
    raw_message_url: Optional[str] = None
    events: list[MessageEvent] = Field(default_factory=list)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "EmailLogMessage":
        """Build from API response (handles 'from' alias and None for events/vars)."""
        payload = dict(data)
        if payload.get("events") is None:
            payload["events"] = []
        else:
            payload["events"] = [_parse_message_event(e) for e in payload["events"]]
        if payload.get("custom_variables") is None:
            payload["custom_variables"] = {}
        if payload.get("template_variables") is None:
            payload["template_variables"] = {}
        return cls(**payload)


@dataclass
class EmailLogsListResponse:
    """Paginated response from list email logs."""

    messages: list[EmailLogMessage]
    total_count: int
    next_page_cursor: Optional[str]


# --- Filters for list (operator + value) ---

# Status and events
StatusValue = Literal["delivered", "not_delivered", "enqueued", "opted_out"]
EventsFilterValue = Literal[
    "delivery",
    "open",
    "click",
    "bounce",
    "spam",
    "unsubscribe",
    "soft_bounce",
    "reject",
    "suspension",
]

# Numeric comparison
FilterOperatorNumeric = Literal["equal", "greater_than", "less_than"]

# Sending stream
SendingStreamValue = Literal["transactional", "bulk"]


def _filter_spec(
    operator: str,
    value: Optional[Union[str, int, list[Any]]] = None,
) -> dict[str, Any]:
    """Build a filter spec dict for API (operator + optional value)."""
    out: dict[str, Any] = {"operator": operator}
    if value is not None:
        out["value"] = value
    return out


# Convenience filter builders (optional; users can also pass raw dicts)


def filter_ci_equal(value: Union[str, list[str]]) -> dict[str, Any]:
    return _filter_spec("ci_equal", value)


def filter_ci_not_equal(value: Union[str, list[str]]) -> dict[str, Any]:
    return _filter_spec("ci_not_equal", value)


def filter_ci_contain(value: str) -> dict[str, Any]:
    return _filter_spec("ci_contain", value)


def filter_ci_not_contain(value: str) -> dict[str, Any]:
    return _filter_spec("ci_not_contain", value)


def filter_status_equal(value: Union[StatusValue, list[StatusValue]]) -> dict[str, Any]:
    return _filter_spec("equal", value)


def filter_status_not_equal(
    value: Union[StatusValue, list[StatusValue]],
) -> dict[str, Any]:
    return _filter_spec("not_equal", value)


def filter_events_include(
    value: Union[EventsFilterValue, list[EventsFilterValue]],
) -> dict[str, Any]:
    return _filter_spec("include_event", value)


def filter_events_not_include(
    value: Union[EventsFilterValue, list[EventsFilterValue]],
) -> dict[str, Any]:
    return _filter_spec("not_include_event", value)


def filter_numeric(
    operator: FilterOperatorNumeric,
    value: int,
) -> dict[str, Any]:
    return _filter_spec(operator, value)


def filter_sending_domain_id_equal(value: Union[int, list[int]]) -> dict[str, Any]:
    return _filter_spec("equal", value)


def filter_sending_domain_id_not_equal(value: Union[int, list[int]]) -> dict[str, Any]:
    return _filter_spec("not_equal", value)


def filter_sending_stream_equal(
    value: Union[SendingStreamValue, list[SendingStreamValue]],
) -> dict[str, Any]:
    return _filter_spec("equal", value)


def filter_sending_stream_not_equal(
    value: Union[SendingStreamValue, list[SendingStreamValue]],
) -> dict[str, Any]:
    return _filter_spec("not_equal", value)


def filter_string_equal(value: Union[str, list[str]]) -> dict[str, Any]:
    return _filter_spec("equal", value)


def filter_string_not_equal(value: Union[str, list[str]]) -> dict[str, Any]:
    return _filter_spec("not_equal", value)


def filter_empty() -> dict[str, Any]:
    return _filter_spec("empty")


def filter_string_not_empty() -> dict[str, Any]:
    return _filter_spec("not_empty")


# --- Email logs list filters (top-level) ---


class EmailLogsListFilters:
    """
    Filters for listing email logs. Pass to email_logs.get_list(filters=...).
    All fields are optional. Date range: sent_after, sent_before (ISO 8601).
    Other fields are filter specs: {"operator": "...", "value": ...} or
    {"operator": "empty"}.
    """

    def __init__(
        self,
        *,
        sent_after: Optional[str] = None,
        sent_before: Optional[str] = None,
        to: Optional[dict[str, Any]] = None,
        from_: Optional[dict[str, Any]] = None,
        subject: Optional[dict[str, Any]] = None,
        status: Optional[dict[str, Any]] = None,
        events: Optional[dict[str, Any]] = None,
        clicks_count: Optional[dict[str, Any]] = None,
        opens_count: Optional[dict[str, Any]] = None,
        client_ip: Optional[dict[str, Any]] = None,
        sending_ip: Optional[dict[str, Any]] = None,
        email_service_provider_response: Optional[dict[str, Any]] = None,
        email_service_provider: Optional[dict[str, Any]] = None,
        recipient_mx: Optional[dict[str, Any]] = None,
        category: Optional[dict[str, Any]] = None,
        sending_domain_id: Optional[dict[str, Any]] = None,
        sending_stream: Optional[dict[str, Any]] = None,
    ) -> None:
        self.sent_after = sent_after
        self.sent_before = sent_before
        self.to = to
        self.from_ = from_
        self.subject = subject
        self.status = status
        self.events = events
        self.clicks_count = clicks_count
        self.opens_count = opens_count
        self.client_ip = client_ip
        self.sending_ip = sending_ip
        self.email_service_provider_response = email_service_provider_response
        self.email_service_provider = email_service_provider
        self.recipient_mx = recipient_mx
        self.category = category
        self.sending_domain_id = sending_domain_id
        self.sending_stream = sending_stream

    def to_params(self) -> dict[str, Any]:
        """Serialize to query params: filters[key] and filters[key][operator]."""
        params: dict[str, Any] = {}
        if self.sent_after is not None:
            params["filters[sent_after]"] = self.sent_after
        if self.sent_before is not None:
            params["filters[sent_before]"] = self.sent_before

        # Map Python-friendly name to API key (from_ -> "from")
        spec_keys = [
            ("to", self.to),
            ("from", self.from_),
            ("subject", self.subject),
            ("status", self.status),
            ("events", self.events),
            ("clicks_count", self.clicks_count),
            ("opens_count", self.opens_count),
            ("client_ip", self.client_ip),
            ("sending_ip", self.sending_ip),
            ("email_service_provider_response", self.email_service_provider_response),
            ("email_service_provider", self.email_service_provider),
            ("recipient_mx", self.recipient_mx),
            ("category", self.category),
            ("sending_domain_id", self.sending_domain_id),
            ("sending_stream", self.sending_stream),
        ]
        for key, spec in spec_keys:
            if spec is None:
                continue
            prefix = f"filters[{key}]"
            if "operator" in spec:
                params[f"{prefix}[operator]"] = spec["operator"]
            if "value" in spec:
                val = spec["value"]
                if isinstance(val, list):
                    # requests serializes list as key=v1&key=v2
                    params[f"{prefix}[value][]"] = val
                else:
                    params[f"{prefix}[value]"] = val
        return params
