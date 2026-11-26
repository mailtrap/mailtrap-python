from datetime import datetime

from pydantic.dataclasses import dataclass

from mailtrap.models.mail.attachment import Disposition


@dataclass
class Attachment:
    id: int
    message_id: int
    filename: str
    attachment_type: Disposition
    content_type: str
    attachment_size: int
    created_at: datetime
    updated_at: datetime
    attachment_human_size: str
    download_path: str
    content_id: str | None = None
    transfer_encoding: str | None = None
