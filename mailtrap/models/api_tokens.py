from typing import Optional
from typing import Union

from pydantic.dataclasses import dataclass


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
