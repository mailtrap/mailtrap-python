from pydantic.dataclasses import dataclass

from mailtrap.models.common import RequestParams
from mailtrap.models.permissions import Permissions


@dataclass
class AccountAccessFilterParams(RequestParams):
    domain_ids: list[str]
    inbox_ids: list[str]
    project_ids: list[str]


@dataclass
class Account:
    id: int
    name: str
    access_levels: list[int]


@dataclass
class Specifier:
    id: int
    email: str
    name: str
    two_factor_authentication_enabled: bool


@dataclass
class AccountAccessResource:
    resource_id: int
    resource_type: str
    access_level: int


@dataclass
class AccountAccess:
    id: int
    specifier_type: str
    specifier: Specifier
    resources: list[AccountAccessResource]
    permissions: Permissions
