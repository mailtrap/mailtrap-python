from typing import Optional

from pydantic.dataclasses import dataclass

from mailtrap.models.common import RequestParams
from mailtrap.models.permissions import Permissions


@dataclass
class Sandbox:
    id: int
    name: str
    username: str
    max_size: int
    status: str
    email_username: str
    email_username_enabled: bool
    sent_messages_count: int
    forwarded_messages_count: int
    used: bool
    forward_from_email_address: str
    project_id: int
    domain: str
    pop3_domain: str
    email_domain: str
    api_domain: str
    emails_count: int
    emails_unread_count: int
    smtp_ports: list[int]
    pop3_ports: list[int]
    max_message_size: int
    permissions: Permissions
    password: Optional[str] = (
        None  # Password is only available if you have admin permissions for the sandbox.
    )
    last_message_sent_at: Optional[str] = None


@dataclass
class CreateSandboxParams(RequestParams):
    name: str


@dataclass
class UpdateSandboxParams(RequestParams):
    name: Optional[str] = None
    email_username: Optional[str] = None

    def __post_init__(self) -> None:
        if all(
            value is None
            for value in [
                self.name,
                self.email_username,
            ]
        ):
            raise ValueError("At least one field must be provided for update action")
