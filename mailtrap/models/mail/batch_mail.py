from typing import Any

from pydantic import Field
from pydantic.dataclasses import dataclass

from mailtrap.models.common import RequestParams
from mailtrap.models.mail.address import Address
from mailtrap.models.mail.attachment import Attachment


@dataclass
class BaseBatchMail(RequestParams):
    sender: Address = Field(..., serialization_alias="from")
    attachments: list[Attachment] | None = None
    headers: dict[str, str] | None = None
    custom_variables: dict[str, Any] | None = None
    reply_to: Address | None = None


@dataclass
class BatchMail(BaseBatchMail):
    subject: str = Field(...)  # type: ignore
    text: str | None = None
    html: str | None = None
    category: str | None = None


@dataclass
class BatchMailFromTemplate(BaseBatchMail):
    template_uuid: str = Field(...)  # type: ignore
    template_variables: dict[str, Any] | None = None


@dataclass
class BatchEmailRequest(BaseBatchMail):
    to: list[Address] = Field(...)  # type: ignore
    sender: Address | None = Field(
        None, serialization_alias="from"
    )  # type: ignore[assignment]
    cc: list[Address] | None = None
    bcc: list[Address] | None = None
    subject: str | None = None
    text: str | None = None
    html: str | None = None
    category: str | None = None
    template_uuid: str | None = None
    template_variables: dict[str, Any] | None = None


@dataclass
class BatchSendEmailParams(RequestParams):
    base: BatchMail | BatchMailFromTemplate
    requests: list[BatchEmailRequest]


@dataclass
class BatchSendResponseItem:
    success: bool
    message_ids: list[str] | None = None
    errors: list[str] | None = None


@dataclass
class BatchSendResponse:
    success: bool
    responses: list[BatchSendResponseItem]
    errors: list[str] | None = None
