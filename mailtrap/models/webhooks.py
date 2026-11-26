from typing import Optional

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
    sending_stream: Optional[str] = None
    domain_id: Optional[int] = None
    inbound_inbox_id: Optional[int] = None
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
    """
    ``event_types`` can include ``subscription_preferences_update``, sent when a
    contact changes their subscription topic preferences. It is available only
    on a ``campaigns`` webhook or an ``email_sending`` one for the ``bulk``
    stream.
    """

    url: str
    webhook_type: str
    active: Optional[bool] = None
    payload_format: Optional[str] = None
    sending_stream: Optional[str] = None
    event_types: Optional[list[str]] = None
    domain_id: Optional[int] = None
    inbound_inbox_id: Optional[int] = None


@dataclass
class UpdateWebhookParams(RequestParams):
    """
    ``event_types`` can include ``subscription_preferences_update`` on a
    ``campaigns`` webhook or an ``email_sending`` one for the ``bulk`` stream.
    """

    url: Optional[str] = None
    active: Optional[bool] = None
    payload_format: Optional[str] = None
    event_types: Optional[list[str]] = None
    inbound_inbox_id: Optional[int] = None
