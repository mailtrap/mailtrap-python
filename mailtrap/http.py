from json import JSONDecodeError
from typing import Any
from typing import NoReturn

from requests import Response
from requests import Session

from mailtrap.config import DEFAULT_REQUEST_TIMEOUT
from mailtrap.exceptions import APIError
from mailtrap.exceptions import AuthorizationError


class HttpClient:
    def __init__(
        self,
        host: str,
        headers: dict[str, str] | None = None,
        timeout: int = DEFAULT_REQUEST_TIMEOUT,
    ):
        self._host = host
        self._session = Session()
        self._session.headers.update(headers or {})
        self._timeout = timeout

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        response = self._session.get(
            self._url(path), params=params, timeout=self._timeout
        )
        return self._process_response(response)

    def post(self, path: str, json: dict[str, Any] | None = None) -> Any:
        response = self._session.post(self._url(path), json=json, timeout=self._timeout)
        return self._process_response(response)

    def put(self, path: str, json: dict[str, Any] | None = None) -> Any:
        response = self._session.put(self._url(path), json=json, timeout=self._timeout)
        return self._process_response(response)

    def patch(self, path: str, json: dict[str, Any] | None = None) -> Any:
        response = self._session.patch(self._url(path), json=json, timeout=self._timeout)
        return self._process_response(response)

    def delete(self, path: str) -> Any:
        response = self._session.delete(self._url(path), timeout=self._timeout)
        return self._process_response(response)

    def _url(self, path: str) -> str:
        return f"https://{self._host}/{path.lstrip('/')}"

    def _process_response(self, response: Response) -> Any:
        if not response.ok:
            self._handle_failed_response(response)

        if not response.content.strip():
            return None

        try:
            return response.json()
        except (JSONDecodeError, ValueError):
            return response.text

    def _handle_failed_response(self, response: Response) -> NoReturn:
        status_code = response.status_code

        if not response.content:
            if status_code == 404:
                raise APIError(status_code, errors=["Not Found"])
            raise APIError(status_code, errors=["Empty response body"])

        try:
            data = response.json()
        except (JSONDecodeError, ValueError) as exc:
            raise APIError(status_code, errors=["Invalid JSON"]) from exc

        errors = self._extract_errors(data)

        if status_code == 401:
            raise AuthorizationError(errors=errors)

        raise APIError(status_code, errors=errors)

    @staticmethod
    def _extract_errors(data: dict[str, Any]) -> list[str]:
        def flatten_errors(errors: Any) -> list[str]:
            if isinstance(errors, list):
                return [str(error) for error in errors]

            if isinstance(errors, dict):
                flat_errors = []
                for key, value in errors.items():
                    if isinstance(value, list):
                        flat_errors.extend([f"{key}: {v}" for v in value])
                    else:
                        flat_errors.append(f"{key}: {value}")
                return flat_errors

            return [str(errors)]

        if "errors" in data:
            return flatten_errors(data["errors"])

        if "error" in data:
            return flatten_errors(data["error"])

        return ["Unknown error"]
