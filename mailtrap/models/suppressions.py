from datetime import datetime

from pydantic.dataclasses import dataclass

from mailtrap.models.common import RequestParams


@dataclass
class Suppression:
    id: str
    type: str
    created_at: datetime
    email: str
    sending_stream: str
    domain_name: str | None = None
    message_bounce_category: str | None = None
    message_category: str | None = None
    message_client_ip: str | None = None
    message_created_at: str | datetime | None = None
    message_esp_response: str | None = None
    message_esp_server_type: str | None = None
    message_outgoing_ip: str | None = None
    message_recipient_mx_name: str | None = None
    message_sender_email: str | None = None
    message_subject: str | None = None


@dataclass
class SuppressionResponse:
    data: Suppression


@dataclass
class CreateSuppressionParams(RequestParams):
    email: str
    domain_id: int
    sending_stream: str
    type: str | None = None
