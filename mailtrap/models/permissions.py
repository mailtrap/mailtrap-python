from typing import Optional

from pydantic.dataclasses import dataclass

from mailtrap.models.common import RequestParams


@dataclass
class Permissions:
    can_read: bool
    can_update: bool
    can_destroy: bool
    can_leave: bool


@dataclass
class PermissionResource:
    id: int
    name: str
    type: str
    access_level: int
    resources: list["PermissionResource"]


@dataclass
class PermissionResourceParams(RequestParams):
    resource_id: str
    resource_type: str
    access_level: Optional[str] = None
    _destroy: Optional[bool] = None


@dataclass
class UpdatePermissionsResponse:
    message: str
