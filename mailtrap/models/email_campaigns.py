"""Models for the Email Campaigns API (campaigns + stats)."""

from typing import Optional

from pydantic import Field
from pydantic.dataclasses import dataclass

from mailtrap.models.common import Pagination
from mailtrap.models.common import RequestParams


@dataclass
class EmailCampaignReplyTo:
    """Reply-To address parts."""

    display_name: Optional[str] = None
    local_part: Optional[str] = None
    domain: Optional[str] = None


@dataclass
class EmailCampaignDeliveryOptions:
    """Delivery throttling options. Applies when ``delivery_mode`` is ``gradual``."""

    emails_per_hour: Optional[int] = None


@dataclass
class EmailCampaignTemplateAttributes:
    """
    Inline email template — the campaign's subject and design. On update only
    the sub-fields you provide change; ``merge_tags`` is replaced as a whole
    when provided.
    """

    subject: Optional[str] = None
    body_html: Optional[str] = None
    body_text: Optional[str] = None
    merge_tags: Optional[list[str]] = None


@dataclass
class CreateEmailCampaignTemplateAttributes:
    """
    Inline email template for creating a campaign — ``subject`` is required;
    the design fields are optional until the campaign is scheduled or started.
    """

    subject: str
    body_html: Optional[str] = None
    body_text: Optional[str] = None
    merge_tags: Optional[list[str]] = None


@dataclass
class EmailCampaignStats:
    """
    Aggregated campaign performance metrics. All counts and rates are ``0``
    when the campaign has not been started.
    """

    delivery_count: Optional[int] = None
    open_count: Optional[int] = None
    click_count: Optional[int] = None
    bounce_count: Optional[int] = None
    unsubscription_count: Optional[int] = None
    sent_count: Optional[int] = None
    spam_count: Optional[int] = None
    delivery_rate: Optional[float] = None
    open_rate: Optional[float] = None
    click_rate: Optional[float] = None
    bounce_rate: Optional[float] = None
    spam_rate: Optional[float] = None
    unsubscription_rate: Optional[float] = None


@dataclass
class CampaignStateError:
    """A per-recipient error recorded when sending failed."""

    message: Optional[str] = None
    rcpt_index: Optional[int] = None


@dataclass
class CurrentStateMetadata:
    """Metadata about the most recent campaign state transition."""

    reason: Optional[str] = None
    error: Optional[str] = None
    scheduled_at: Optional[str] = None
    errors: list[CampaignStateError] = Field(default_factory=list)


@dataclass
class EmailCampaignTemplate:
    """
    The campaign's template as returned by the API. ``body_html`` and
    ``body_text`` are returned only on single-campaign responses; the list
    endpoint omits them.
    """

    id: Optional[int] = None
    subject: Optional[str] = None
    merge_tags: list[str] = Field(default_factory=list)
    body_html: Optional[str] = None
    body_text: Optional[str] = None


@dataclass
class EmailCampaign:
    """A single email campaign."""

    id: int
    domain_id: Optional[int] = None
    domain_name: Optional[str] = None
    name: Optional[str] = None
    from_local_part: Optional[str] = None
    from_display_name: Optional[str] = None
    reply_to: Optional[EmailCampaignReplyTo] = None
    current_state: Optional[str] = None
    current_state_metadata: Optional[CurrentStateMetadata] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    last_started_at: Optional[str] = None
    last_started_at_date: Optional[str] = None
    recipient_total_count: Optional[int] = None
    contact_list_ids: list[int] = Field(default_factory=list)
    contact_segment_ids: list[int] = Field(default_factory=list)
    delivery_mode: Optional[str] = None
    delivery_options: Optional[EmailCampaignDeliveryOptions] = None
    subscription_topic_id: Optional[int] = None
    template: Optional[EmailCampaignTemplate] = None


@dataclass
class EmailCampaignResponse:
    """Envelope of a single-campaign response."""

    data: EmailCampaign


@dataclass
class EmailCampaignStatsResponse:
    """Envelope of the campaign stats response."""

    data: EmailCampaignStats


@dataclass
class EmailCampaignListResponse:
    """Paginated response from listing email campaigns."""

    data: list[EmailCampaign] = Field(default_factory=list)
    pagination: Optional[Pagination] = None


@dataclass
class EmailCampaignListParams(RequestParams):
    """
    Query params for listing email campaigns. ``search`` filters by name and
    serializes to the ``search`` wire parameter.
    """

    per_page: Optional[int] = None
    search: Optional[str] = None
    token: Optional[int] = None


@dataclass
class EmailCampaignStatsParams(RequestParams):
    """Query params for campaign stats (``YYYY-MM-DD`` aggregation window)."""

    start_date: Optional[str] = None
    end_date: Optional[str] = None


@dataclass
class CreateEmailCampaignParams(RequestParams):
    """
    Attributes for creating an email campaign (sent as a flat JSON body).
    The campaign is always created in the ``draft`` state.
    ``subscription_topic_id`` is the subscription topic the campaign is sent
    under; it must cover the campaign's domain.
    """

    name: str
    domain_id: int
    from_local_part: str
    template_attributes: CreateEmailCampaignTemplateAttributes
    from_display_name: Optional[str] = None
    reply_to: Optional[EmailCampaignReplyTo] = None
    delivery_mode: Optional[str] = None
    delivery_options: Optional[EmailCampaignDeliveryOptions] = None
    contact_list_ids: Optional[list[int]] = None
    contact_segment_ids: Optional[list[int]] = None
    subscription_topic_id: Optional[int] = None


@dataclass
class UpdateEmailCampaignParams(RequestParams):
    """
    Attributes for updating a draft email campaign (sent as a flat JSON body).
    All fields are optional; only provided fields are changed. A campaign's
    ``subscription_topic_id`` can be changed but not removed.
    """

    name: Optional[str] = None
    domain_id: Optional[int] = None
    from_local_part: Optional[str] = None
    from_display_name: Optional[str] = None
    reply_to: Optional[EmailCampaignReplyTo] = None
    template_attributes: Optional[EmailCampaignTemplateAttributes] = None
    delivery_mode: Optional[str] = None
    delivery_options: Optional[EmailCampaignDeliveryOptions] = None
    contact_list_ids: Optional[list[int]] = None
    contact_segment_ids: Optional[list[int]] = None
    subscription_topic_id: Optional[int] = None


@dataclass
class ScheduleEmailCampaignParams(RequestParams):
    """
    When to start sending the campaign. ``datetime`` is an ISO 8601 timestamp
    that must be in the future and no more than 1 month ahead.
    """

    datetime: str
