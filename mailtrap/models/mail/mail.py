from typing import Any
from typing import Optional

from pydantic import Field
from pydantic.dataclasses import dataclass

from mailtrap.models.common import RequestParams
from mailtrap.models.mail.address import Address
from mailtrap.models.mail.attachment import Attachment


@dataclass
class BaseMail(RequestParams):
    to: list[Address]
    sender: Address = Field(..., serialization_alias="from")
    cc: Optional[list[Address]] = None
    bcc: Optional[list[Address]] = None
    attachments: Optional[list[Attachment]] = None
    headers: Optional[dict[str, str]] = None
    custom_variables: Optional[dict[str, Any]] = None
    reply_to: Optional[Address] = None


@dataclass
class Mail(BaseMail):
    subject: str = Field(...)  # type:ignore
    text: Optional[str] = None
    html: Optional[str] = None
    category: Optional[str] = None


@dataclass
class MailFromTemplate(BaseMail):
    template_uuid: str = Field(...)  # type:ignore
    template_variables: Optional[dict[str, Any]] = None


@dataclass
class SendingMailResponse:
    success: bool
    message_ids: list[str]
