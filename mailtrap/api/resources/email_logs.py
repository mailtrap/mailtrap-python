"""Email Logs API resource - list and get email sending logs."""

from typing import Optional

from mailtrap.http import HttpClient
from mailtrap.models.email_logs import EmailLogMessage
from mailtrap.models.email_logs import EmailLogsListFilters
from mailtrap.models.email_logs import EmailLogsListResponse


class EmailLogsApi:
    def __init__(self, client: HttpClient, account_id: str) -> None:
        self._account_id = account_id
        self._client = client

    def get_list(
        self,
        filters: Optional[EmailLogsListFilters] = None,
        search_after: Optional[str] = None,
    ) -> EmailLogsListResponse:
        """
        List email logs (paginated). Results are ordered by sent_at descending.
        Use search_after with next_page_cursor from the previous response for
        the next page.
        """
        params: dict[str, object] = {}
        if filters is not None:
            params.update(filters.to_params())
        if search_after is not None:
            params["search_after"] = search_after
        response = self._client.get(self._api_path(), params=params or None)
        if not isinstance(response, dict):
            response = {}
        raw_messages = response.get("messages", [])
        messages = [EmailLogMessage.from_api(msg) for msg in raw_messages]
        return EmailLogsListResponse(
            messages=messages,
            total_count=response.get("total_count", 0),
            next_page_cursor=response.get("next_page_cursor"),
        )

    def get_by_id(self, sending_message_id: str) -> EmailLogMessage:
        """Get a single email log message by its UUID."""
        response = self._client.get(self._api_path(sending_message_id))
        if not isinstance(response, dict):
            raise ValueError(
                "Email Logs API returned unexpected response for message "
                f"{sending_message_id!r}: expected a JSON object, got "
                f"{type(response).__name__}: {response!r}"
            )
        return EmailLogMessage.from_api(response)

    def _api_path(self, sending_message_id: Optional[str] = None) -> str:
        path = f"/api/accounts/{self._account_id}/email_logs"
        if sending_message_id is not None:
            path = f"{path}/{sending_message_id}"
        return path
