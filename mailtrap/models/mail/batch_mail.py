from typing import Any
from typing import Optional
from typing import Union

from pydantic import Field
from pydantic.dataclasses import dataclass

from mailtrap.models.common import RequestParams
from mailtrap.models.mail.address import Address
from mailtrap.models.mail.attachment import Attachment


@dataclass
class BaseBatchMail(RequestParams):
    sender: Address = Field(..., serialization_alias="from")
    attachments: Optional[list[Attachment]] = None
    headers: Optional[dict[str, str]] = None
    custom_variables: Optional[dict[str, Any]] = None
    reply_to: Optional[Address] = None


@dataclass
class BatchMail(BaseBatchMail):
    subject: str = Field(...)  # type:ignore
    text: Optional[str] = None
    html: Optional[str] = None
    category: Optional[str] = None


@dataclass
class BatchMailFromTemplate(BaseBatchMail):
    template_uuid: str = Field(...)  # type:ignore
    template_variables: Optional[dict[str, Any]] = None


@dataclass
class BatchEmailRequest(BaseBatchMail):
    to: list[Address] = Field(...)  # type:ignore
    sender: Optional[Address] = Field(
        None, serialization_alias="from"
    )  # type: ignore[assignment]
    cc: Optional[list[Address]] = None
    bcc: Optional[list[Address]] = None
    subject: Optional[str] = None
    text: Optional[str] = None
    html: Optional[str] = None
    category: Optional[str] = None
    template_uuid: Optional[str] = None
    template_variables: Optional[dict[str, Any]] = None


@dataclass
class BatchSendEmailParams(RequestParams):
    base: Union[BatchMail, BatchMailFromTemplate]
    requests: list[BatchEmailRequest]


@dataclass
class BatchSendResponseItem:
    success: bool
    message_ids: Optional[list[str]] = None
    errors: Optional[list[str]] = None


@dataclass
class BatchSendResponse:
    success: bool
    responses: list[BatchSendResponseItem]
    errors: Optional[list[str]] = None
