from datetime import datetime
from typing import Any
from typing import Optional
from typing import Union

from pydantic.dataclasses import dataclass

from mailtrap.models.common import RequestParams


@dataclass
class CreateContactFieldParams(RequestParams):
    name: str
    data_type: str
    merge_tag: str


@dataclass
class UpdateContactFieldParams(RequestParams):
    name: Optional[str] = None
    merge_tag: Optional[str] = None

    def __post_init__(self) -> None:
        if all(value is None for value in [self.name, self.merge_tag]):
            raise ValueError("At least one field must be provided for update action")


@dataclass
class ContactField:
    id: int
    name: str
    data_type: str
    merge_tag: str


@dataclass
class ContactListParams(RequestParams):
    name: str


@dataclass
class ContactList:
    id: int
    name: str


@dataclass
class CreateContactParams(RequestParams):
    email: str
    fields: Optional[dict[str, Union[str, int, float, bool]]] = (
        None  # field_merge_tag: value
    )
    list_ids: Optional[list[int]] = None


@dataclass
class UpdateContactParams(RequestParams):
    email: Optional[str] = None
    fields: Optional[dict[str, Union[str, int, float, bool]]] = (
        None  # field_merge_tag: value
    )
    list_ids_included: Optional[list[int]] = None
    list_ids_excluded: Optional[list[int]] = None
    unsubscribed: Optional[bool] = None

    def __post_init__(self) -> None:
        if all(
            value is None
            for value in [
                self.email,
                self.fields,
                self.list_ids_included,
                self.list_ids_excluded,
                self.unsubscribed,
            ]
        ):
            raise ValueError("At least one field must be provided for update action")


@dataclass
class Contact:
    id: str
    email: str
    fields: dict[str, Union[str, int, float, bool]]  # field_merge_tag: value
    list_ids: list[int]
    status: str
    created_at: int
    updated_at: int


@dataclass
class ContactResponse:
    data: Contact


@dataclass
class ContactImport:
    id: int
    status: str
    created_contacts_count: Optional[int] = None
    updated_contacts_count: Optional[int] = None
    contacts_over_limit_count: Optional[int] = None


@dataclass
class ImportContactParams(RequestParams):
    email: str
    fields: Optional[dict[str, Union[str, int, float, bool]]] = (
        None  # field_merge_tag: value
    )
    list_ids_included: Optional[list[int]] = None
    list_ids_excluded: Optional[list[int]] = None


@dataclass
class ContactExportFilter(RequestParams):
    name: str
    operator: str
    value: list[int]


@dataclass
class CreateContactExportParams(RequestParams):
    filters: list[ContactExportFilter]


@dataclass
class ContactExportDetail:
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    url: Optional[str] = None


@dataclass
class ContactEventParams(RequestParams):
    name: str
    params: Optional[dict[str, Any]] = None


@dataclass
class ContactEvent:
    contact_id: str
    contact_email: str
    name: str
    params: Optional[dict[str, Any]] = None
