from typing import Optional
from typing import Union

from pydantic import Field
from pydantic.dataclasses import dataclass

from mailtrap.models.common import RequestParams


@dataclass
class ApiTokenResource:
    resource_type: str
    resource_id: Union[int, str]
    access_level: int


@dataclass
class ApiToken:
    id: int
    name: str
    last_4_digits: str
    created_by: str
    expires_at: Optional[str]
    resources: list[ApiTokenResource]


@dataclass
class ApiTokenWithToken(ApiToken):
    token: str = ""


@dataclass
class CreateApiTokenParams(RequestParams):
    name: str
    resources: list[ApiTokenResource] = Field(default_factory=list)
