from datetime import datetime
from typing import Optional
from typing import Union

from pydantic.dataclasses import dataclass

from mailtrap.models.common import RequestParams


@dataclass
class Suppression:
    id: str
    type: str
    created_at: datetime
    email: str
    sending_stream: str
    domain_name: Optional[str] = None
    # Set on a "topic unsubscription", the topic the contact unsubscribed from.
    subscription_topic_id: Optional[int] = None
    message_bounce_category: Optional[str] = None
    message_category: Optional[str] = None
    message_client_ip: Optional[str] = None
    message_created_at: Optional[Union[str, datetime]] = None
    message_esp_response: Optional[str] = None
    message_esp_server_type: Optional[str] = None
    message_outgoing_ip: Optional[str] = None
    message_recipient_mx_name: Optional[str] = None
    message_sender_email: Optional[str] = None
    message_subject: Optional[str] = None


@dataclass
class SuppressionResponse:
    data: Suppression


@dataclass
class CreateSuppressionParams(RequestParams):
    email: str
    domain_id: int
    sending_stream: str
    type: Optional[str] = None  # not "topic unsubscription", which can't be created
