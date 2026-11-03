from typing import Optional

from pydantic.dataclasses import dataclass

from mailtrap.models.common import RequestParams
from mailtrap.models.permissions import Permissions
from mailtrap.models.sandboxes import Sandbox


@dataclass
class ShareLinks:
    admin: str
    viewer: str


@dataclass
class Project:
    id: int
    name: str
    inboxes: list[Sandbox]
    permissions: Permissions
    share_links: Optional[ShareLinks] = None


@dataclass
class ProjectParams(RequestParams):
    name: str
