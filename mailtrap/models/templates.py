from pydantic.dataclasses import dataclass

from mailtrap.models.common import RequestParams


@dataclass
class CreateEmailTemplateParams(RequestParams):
    name: str
    subject: str
    category: str
    body_text: str | None = None
    body_html: str | None = None


@dataclass
class UpdateEmailTemplateParams(RequestParams):
    name: str | None = None
    subject: str | None = None
    category: str | None = None
    body_text: str | None = None
    body_html: str | None = None

    def __post_init__(self) -> None:
        if all(
            value is None
            for value in [
                self.name,
                self.subject,
                self.category,
                self.body_text,
                self.body_html,
            ]
        ):
            raise ValueError("At least one field must be provided for update action")


@dataclass
class EmailTemplate:
    id: int
    name: str
    uuid: str
    category: str
    subject: str
    body_text: str | None
    body_html: str | None
    created_at: str
    updated_at: str
