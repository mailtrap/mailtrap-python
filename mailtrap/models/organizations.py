from pydantic.dataclasses import dataclass

from mailtrap.models.common import RequestParams


@dataclass
class SubAccount:
    id: int
    name: str


@dataclass
class CreateSubAccountParams(RequestParams):
    name: str
