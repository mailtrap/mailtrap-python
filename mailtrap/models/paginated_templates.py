"""Models for the account-scoped, paginated Templates API (``/api/templates``)."""

from pydantic import Field
from pydantic.dataclasses import dataclass

from mailtrap.models.common import Pagination
from mailtrap.models.common import RequestParams


@dataclass
class Template:
    """A single email template."""

    id: int
    uuid: str | None = None
    name: str | None = None
    category: str | None = None
    subject: str | None = None
    body_html: str | None = None
    body_text: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


@dataclass
class TemplateResponse:
    """Envelope of a single-template response."""

    data: Template


@dataclass
class TemplateListResponse:
    """Paginated response from listing templates."""

    data: list[Template] = Field(default_factory=list)
    pagination: Pagination | None = None


@dataclass
class TemplateListParams(RequestParams):
    """
    Query params for listing templates. ``token`` is the page number and
    ``per_page`` is capped at 100.
    """

    per_page: int | None = None
    token: int | None = None


@dataclass
class CreateTemplateParams(RequestParams):
    """Attributes for creating a template (sent as a flat JSON body)."""

    name: str
    subject: str
    category: str
    body_html: str | None = None
    body_text: str | None = None


@dataclass
class UpdateTemplateParams(RequestParams):
    """
    Attributes for updating a template (sent as a flat JSON body). All fields
    are optional, but at least one must be provided.
    """

    name: str | None = None
    subject: str | None = None
    category: str | None = None
    body_html: str | None = None
    body_text: str | None = None

    def __post_init__(self) -> None:
        if all(
            value is None
            for value in [
                self.name,
                self.subject,
                self.category,
                self.body_html,
                self.body_text,
            ]
        ):
            raise ValueError("At least one field must be provided for update action")
