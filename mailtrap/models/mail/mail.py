from typing import Any

from pydantic import Field
from pydantic.dataclasses import dataclass

from mailtrap.models.common import RequestParams
from mailtrap.models.mail.address import Address
from mailtrap.models.mail.attachment import Attachment


@dataclass
class BaseMail(RequestParams):
    to: list[Address]
    sender: Address = Field(..., serialization_alias="from")
    cc: list[Address] | None = None
    bcc: list[Address] | None = None
    attachments: list[Attachment] | None = None
    headers: dict[str, str] | None = None
    custom_variables: dict[str, Any] | None = None
    reply_to: Address | None = None


@dataclass
class Mail(BaseMail):
    subject: str = Field(...)  # type: ignore
    text: str | None = None
    html: str | None = None
    category: str | None = None


@dataclass
class MailFromTemplate(BaseMail):
    template_uuid: str = Field(...)  # type: ignore
    template_variables: dict[str, Any] | None = None


@dataclass
class SendingMailResponse:
    success: bool
    message_ids: list[str]
