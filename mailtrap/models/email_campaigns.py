"""Models for the Email Campaigns API (campaigns + stats)."""

from typing import Optional

from pydantic import Field
from pydantic.dataclasses import dataclass

from mailtrap.models.common import RequestParams


@dataclass
class ReplyTo:
    """Reply-To address parts."""

    display_name: Optional[str] = None
    local_part: Optional[str] = None
    domain: Optional[str] = None


@dataclass
class EmailCampaignStats:
    """
    Aggregated campaign performance metrics. All counts and rates are ``0``
    when the campaign has not been started. The same shape is returned both
    inline on an ``EmailCampaign`` (its ``stats`` member) and as the standalone
    ``/stats`` response.
    """

    delivery_count: Optional[int] = None
    open_count: Optional[int] = None
    click_count: Optional[int] = None
    bounce_count: Optional[int] = None
    unsubscription_count: Optional[int] = None
    sent_count: Optional[int] = None
    spam_count: Optional[int] = None
    message_count: Optional[int] = None
    reject_count: Optional[int] = None
    delivery_rate: Optional[float] = None
    open_rate: Optional[float] = None
    click_rate: Optional[float] = None
    bounce_rate: Optional[float] = None
    spam_rate: Optional[float] = None
    unsubscription_rate: Optional[float] = None


@dataclass
class CurrentStateMetadata:
    """Metadata about the most recent campaign state transition."""

    reason: Optional[str] = None
    error: Optional[str] = None
    scheduled_at: Optional[str] = None
    errors: list[str] = Field(default_factory=list)


@dataclass
class DeliveryOptions:
    """Delivery throttling options."""

    emails_per_hour: Optional[int] = None


@dataclass
class CampaignTemplate:
    """The campaign template reference."""

    id: Optional[int] = None
    subject: Optional[str] = None


@dataclass
class EmailCampaign:
    """A single email campaign."""

    id: int
    type: Optional[str] = None
    mailsend_domain_id: Optional[int] = None
    mailsend_domain_name: Optional[str] = None
    name: Optional[str] = None
    from_local_part: Optional[str] = None
    from_display_name: Optional[str] = None
    reply_to: Optional[ReplyTo] = None
    current_state: Optional[str] = None
    current_state_metadata: Optional[CurrentStateMetadata] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    last_started_at: Optional[str] = None
    last_started_at_date: Optional[str] = None
    recipient_total_count: Optional[int] = None
    delivery_mode: Optional[str] = None
    delivery_options: Optional[DeliveryOptions] = None
    scheduled_for: Optional[str] = None
    # Omitted from list items.
    audience_defined: Optional[bool] = None
    # Present only when the campaign carries stats.
    stats: Optional[EmailCampaignStats] = None
    template: Optional[CampaignTemplate] = None


@dataclass
class Pagination:
    """Page-token pagination metadata."""

    token: Optional[int] = None
    prev_token: Optional[int] = None
    next_token: Optional[int] = None
    first_url: Optional[str] = None
    prev_url: Optional[str] = None
    current_url: Optional[str] = None
    next_url: Optional[str] = None


@dataclass
class EmailCampaignListResponse:
    """Paginated response from listing email campaigns."""

    data: list[EmailCampaign] = Field(default_factory=list)
    pagination: Optional[Pagination] = None


@dataclass
class EmailCampaignListParams(RequestParams):
    """
    Query params for listing email campaigns. ``search`` filters by name
    (case-insensitive partial match) and serializes to the ``search`` wire
    parameter.
    """

    per_page: Optional[int] = None
    search: Optional[str] = None
    token: Optional[int] = None


@dataclass
class CreateEmailCampaignParams(RequestParams):
    """Attributes for creating an email campaign (wrapped under ``email_campaign``)."""

    name: str
    mailsend_domain_id: int
    from_display_name: Optional[str] = None
    from_local_part: Optional[str] = None
    reply_to: Optional[ReplyTo] = None
    template_attributes: Optional[CampaignTemplate] = None


@dataclass
class UpdateEmailCampaignParams(RequestParams):
    """
    Attributes for updating an email campaign (wrapped under ``email_campaign``).
    All fields are optional; only provided fields are changed.
    """

    name: Optional[str] = None
    mailsend_domain_id: Optional[int] = None
    from_display_name: Optional[str] = None
    from_local_part: Optional[str] = None
    delivery_mode: Optional[str] = None
    scheduled_for: Optional[str] = None
    delivery_options: Optional[DeliveryOptions] = None
    reply_to: Optional[ReplyTo] = None
    template_attributes: Optional[CampaignTemplate] = None
