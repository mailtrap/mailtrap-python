"""Models for the Email Campaigns API (campaigns + stats)."""

from pydantic import Field
from pydantic.dataclasses import dataclass

from mailtrap.models.common import Pagination
from mailtrap.models.common import RequestParams


@dataclass
class EmailCampaignReplyTo:
    """Reply-To address parts."""

    display_name: str | None = None
    local_part: str | None = None
    domain: str | None = None


@dataclass
class EmailCampaignDeliveryOptions:
    """Delivery throttling options. Applies when ``delivery_mode`` is ``gradual``."""

    emails_per_hour: int | None = None


@dataclass
class EmailCampaignTemplateAttributes:
    """
    Inline email template — the campaign's subject and design. On update only
    the sub-fields you provide change; ``merge_tags`` is replaced as a whole
    when provided.
    """

    subject: str | None = None
    body_html: str | None = None
    body_text: str | None = None
    merge_tags: list[str] | None = None


@dataclass
class CreateEmailCampaignTemplateAttributes:
    """
    Inline email template for creating a campaign — ``subject`` is required;
    the design fields are optional until the campaign is scheduled or started.
    """

    subject: str
    body_html: str | None = None
    body_text: str | None = None
    merge_tags: list[str] | None = None


@dataclass
class EmailCampaignStats:
    """
    Aggregated campaign performance metrics. All counts and rates are ``0``
    when the campaign has not been started.
    """

    delivery_count: int | None = None
    open_count: int | None = None
    click_count: int | None = None
    bounce_count: int | None = None
    unsubscription_count: int | None = None
    sent_count: int | None = None
    spam_count: int | None = None
    delivery_rate: float | None = None
    open_rate: float | None = None
    click_rate: float | None = None
    bounce_rate: float | None = None
    spam_rate: float | None = None
    unsubscription_rate: float | None = None


@dataclass
class CampaignStateError:
    """A per-recipient error recorded when sending failed."""

    message: str | None = None
    rcpt_index: int | None = None


@dataclass
class CurrentStateMetadata:
    """Metadata about the most recent campaign state transition."""

    reason: str | None = None
    error: str | None = None
    scheduled_at: str | None = None
    errors: list[CampaignStateError] = Field(default_factory=list)


@dataclass
class EmailCampaignTemplate:
    """
    The campaign's template as returned by the API. ``body_html`` and
    ``body_text`` are returned only on single-campaign responses; the list
    endpoint omits them.
    """

    id: int | None = None
    subject: str | None = None
    merge_tags: list[str] = Field(default_factory=list)
    body_html: str | None = None
    body_text: str | None = None


@dataclass
class EmailCampaign:
    """A single email campaign."""

    id: int
    domain_id: int | None = None
    domain_name: str | None = None
    name: str | None = None
    from_local_part: str | None = None
    from_display_name: str | None = None
    reply_to: EmailCampaignReplyTo | None = None
    current_state: str | None = None
    current_state_metadata: CurrentStateMetadata | None = None
    created_at: str | None = None
    updated_at: str | None = None
    last_started_at: str | None = None
    last_started_at_date: str | None = None
    recipient_total_count: int | None = None
    contact_list_ids: list[int] = Field(default_factory=list)
    contact_segment_ids: list[int] = Field(default_factory=list)
    delivery_mode: str | None = None
    delivery_options: EmailCampaignDeliveryOptions | None = None
    template: EmailCampaignTemplate | None = None


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
    pagination: Pagination | None = None


@dataclass
class EmailCampaignListParams(RequestParams):
    """
    Query params for listing email campaigns. ``search`` filters by name and
    serializes to the ``search`` wire parameter.
    """

    per_page: int | None = None
    search: str | None = None
    token: int | None = None


@dataclass
class EmailCampaignStatsParams(RequestParams):
    """Query params for campaign stats (``YYYY-MM-DD`` aggregation window)."""

    start_date: str | None = None
    end_date: str | None = None


@dataclass
class CreateEmailCampaignParams(RequestParams):
    """
    Attributes for creating an email campaign (sent as a flat JSON body).
    The campaign is always created in the ``draft`` state.
    """

    name: str
    domain_id: int
    from_local_part: str
    template_attributes: CreateEmailCampaignTemplateAttributes
    from_display_name: str | None = None
    reply_to: EmailCampaignReplyTo | None = None
    delivery_mode: str | None = None
    delivery_options: EmailCampaignDeliveryOptions | None = None
    contact_list_ids: list[int] | None = None
    contact_segment_ids: list[int] | None = None


@dataclass
class UpdateEmailCampaignParams(RequestParams):
    """
    Attributes for updating a draft email campaign (sent as a flat JSON body).
    All fields are optional; only provided fields are changed.
    """

    name: str | None = None
    domain_id: int | None = None
    from_local_part: str | None = None
    from_display_name: str | None = None
    reply_to: EmailCampaignReplyTo | None = None
    template_attributes: EmailCampaignTemplateAttributes | None = None
    delivery_mode: str | None = None
    delivery_options: EmailCampaignDeliveryOptions | None = None
    contact_list_ids: list[int] | None = None
    contact_segment_ids: list[int] | None = None


@dataclass
class ScheduleEmailCampaignParams(RequestParams):
    """
    When to start sending the campaign. ``datetime`` is an ISO 8601 timestamp
    that must be in the future and no more than 1 month ahead.
    """

    datetime: str
