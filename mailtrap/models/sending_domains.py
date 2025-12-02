from typing import Optional

from pydantic import Field
from pydantic.dataclasses import dataclass

from mailtrap.models.common import RequestParams


@dataclass
class SendingDomainPermissions:
    can_read: bool
    can_update: bool
    can_destroy: bool


@dataclass
class DnsRecord:
    key: str
    domain: str
    type: str
    value: str
    status: str
    name: str


@dataclass
class SendingDomain:
    id: int
    domain_name: str
    demo: bool
    compliance_status: str
    dns_verified: bool
    open_tracking_enabled: bool
    click_tracking_enabled: bool
    auto_unsubscribe_link_enabled: bool
    custom_domain_tracking_enabled: bool
    health_alerts_enabled: bool
    critical_alerts_enabled: bool
    permissions: SendingDomainPermissions
    alert_recipient_email: Optional[str] = None
    dns_verified_at: Optional[str] = None
    dns_records: list[DnsRecord] = Field(default_factory=list)


@dataclass
class CreateSendingDomainParams(RequestParams):
    domain_name: str


@dataclass
class SendSetupInstructionsParams(RequestParams):
    email: str


@dataclass
class SendSetupInstructionsResponse:
    message: str
