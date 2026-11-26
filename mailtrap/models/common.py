from typing import Any
from typing import Optional
from typing import TypeVar
from typing import cast

from pydantic import GetCoreSchemaHandler
from pydantic import TypeAdapter
from pydantic.dataclasses import dataclass
from pydantic_core import core_schema

T = TypeVar("T", bound="RequestParams")


class UnsetType:
    """
    Sentinel type for request fields that should be omitted from the payload.

    api_data drops fields whose value is UNSET at any depth, keeping an
    omitted field distinct from an explicit None value.
    """

    _instance: Optional["UnsetType"] = None

    def __new__(cls) -> "UnsetType":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "UNSET"

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.is_instance_schema(
            cls,
            serialization=core_schema.plain_serializer_function_ser_schema(
                cls._serialize
            ),
        )

    @staticmethod
    def _serialize(value: "UnsetType") -> "UnsetType":
        return value


UNSET = UnsetType()


def _drop_unset(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _drop_unset(item)
            for key, item in value.items()
            if not isinstance(item, UnsetType)
        }
    # tuples are normalized to lists: api_data feeds json= and api_query_params,
    # both of which expect lists, and JSON has no separate tuple form anyway.
    if isinstance(value, (list, tuple)):
        return [_drop_unset(item) for item in value if not isinstance(item, UnsetType)]
    return value


@dataclass
class RequestParams:
    @property
    def api_data(self: T) -> dict[str, Any]:
        data = cast(
            dict[str, Any],
            TypeAdapter(type(self)).dump_python(self, by_alias=True, exclude_none=True),
        )
        return cast(dict[str, Any], _drop_unset(data))

    @property
    def api_query_params(self: T) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in self.api_data.items():
            if isinstance(value, list):
                result[f"{key}[]"] = value
            else:
                result[key] = value
        return result


@dataclass
class DeletedObject:
    id: int | str


@dataclass
class Pagination:
    """Page-token pagination metadata returned with a paginated list response."""

    token: int | None = None
    prev_token: int | None = None
    next_token: int | None = None
    first_url: str | None = None
    prev_url: str | None = None
    current_url: str | None = None
    next_url: str | None = None
