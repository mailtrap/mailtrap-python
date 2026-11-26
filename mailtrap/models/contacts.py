from datetime import datetime
from typing import Any

from pydantic.dataclasses import dataclass

from mailtrap.models.common import RequestParams


@dataclass
class CreateContactFieldParams(RequestParams):
    name: str
    data_type: str
    merge_tag: str


@dataclass
class UpdateContactFieldParams(RequestParams):
    name: str | None = None
    merge_tag: str | None = None

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
class ContactListsFilterParams(RequestParams):
    # Filter contact lists by name (case-insensitive prefix match).
    search: str | None = None


@dataclass
class ContactList:
    id: int
    name: str


@dataclass
class CreateContactParams(RequestParams):
    email: str
    fields: dict[str, str | int | float | bool] | None = None  # field_merge_tag: value
    list_ids: list[int] | None = None


@dataclass
class UpdateContactParams(RequestParams):
    email: str | None = None
    fields: dict[str, str | int | float | bool] | None = None  # field_merge_tag: value
    list_ids_included: list[int] | None = None
    list_ids_excluded: list[int] | None = None
    unsubscribed: bool | None = None

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
    fields: dict[str, str | int | float | bool]  # field_merge_tag: value
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
    created_contacts_count: int | None = None
    updated_contacts_count: int | None = None
    contacts_over_limit_count: int | None = None


@dataclass
class ImportContactParams(RequestParams):
    email: str
    fields: dict[str, str | int | float | bool] | None = None  # field_merge_tag: value
    list_ids_included: list[int] | None = None
    list_ids_excluded: list[int] | None = None


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
    url: str | None = None


@dataclass
class ContactEventParams(RequestParams):
    name: str
    params: dict[str, Any] | None = None


@dataclass
class ContactEvent:
    contact_id: str
    contact_email: str
    name: str
    params: dict[str, Any] | None = None
