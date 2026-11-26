from pydantic import Field
from pydantic.dataclasses import dataclass

from mailtrap.models.common import RequestParams


@dataclass
class DomainPermissions:
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
class Domain:
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
    permissions: DomainPermissions
    alert_recipient_email: str | None = None
    dns_verified_at: str | None = None
    dns_records: list[DnsRecord] = Field(default_factory=list)
    tracking_opt_out_enabled: bool | None = None
    inbound_enabled: bool | None = None
    inbound_verified: bool | None = None


@dataclass
class CreateDomainParams(RequestParams):
    domain_name: str


@dataclass
class UpdateDomainParams(RequestParams):
    open_tracking_enabled: bool | None = None
    click_tracking_enabled: bool | None = None
    tracking_opt_out_enabled: bool | None = None
    auto_unsubscribe_link_enabled: bool | None = None
    inbound_enabled: bool | None = None


@dataclass
class SendSetupInstructionsParams(RequestParams):
    email: str


@dataclass
class SendSetupInstructionsResponse:
    message: str
