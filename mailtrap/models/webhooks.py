from pydantic import Field
from pydantic.dataclasses import dataclass

from mailtrap.models.common import RequestParams


@dataclass
class Webhook:
    id: int
    url: str
    active: bool
    webhook_type: str
    payload_format: str
    sending_stream: str | None = None
    domain_id: int | None = None
    inbound_inbox_id: int | None = None
    event_types: list[str] = Field(default_factory=list)


@dataclass
class WebhookWithSecret(Webhook):
    signing_secret: str = ""


@dataclass
class WebhookResponse:
    data: Webhook


@dataclass
class WebhookCreateResponse:
    data: WebhookWithSecret


@dataclass
class WebhookListResponse:
    data: list[Webhook] = Field(default_factory=list)


@dataclass
class CreateWebhookParams(RequestParams):
    url: str
    webhook_type: str
    active: bool | None = None
    payload_format: str | None = None
    sending_stream: str | None = None
    event_types: list[str] | None = None
    domain_id: int | None = None
    inbound_inbox_id: int | None = None


@dataclass
class UpdateWebhookParams(RequestParams):
    url: str | None = None
    active: bool | None = None
    payload_format: str | None = None
    event_types: list[str] | None = None
    inbound_inbox_id: int | None = None
