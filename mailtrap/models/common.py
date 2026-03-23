from typing import Any
from typing import TypeVar
from typing import Union
from typing import cast

from pydantic import TypeAdapter
from pydantic.dataclasses import dataclass

T = TypeVar("T", bound="RequestParams")


@dataclass
class RequestParams:
    @property
    def api_data(self: T) -> dict[str, Any]:
        return cast(
            dict[str, Any],
            TypeAdapter(type(self)).dump_python(self, by_alias=True, exclude_none=True),
        )

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
    id: Union[int, str]
