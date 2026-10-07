from typing import Any
from typing import Optional

from mailtrap.http import HttpClient
from mailtrap.models.common import DeletedObject
from mailtrap.models.inbound import InboundThread
from mailtrap.models.inbound import InboundThreadsListResponse


class InboundThreadsApi:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def get_list(
        self,
        inbox_id: int,
        last_id: Optional[str] = None,
        search: Optional[str] = None,
    ) -> InboundThreadsListResponse:
        """
        List conversation threads in an inbox. Pass last_id from a previous
        response to fetch the next page.
        """
        params: dict[str, Any] = {}
        if last_id:
            params["last_id"] = last_id
        if search:
            params["search"] = search
        response = self._client.get(self._api_path(inbox_id), params=params or None)
        return InboundThreadsListResponse(**response)

    def get_by_id(self, inbox_id: int, thread_id: str) -> InboundThread:
        """Get a single thread with its messages embedded (oldest first)."""
        response = self._client.get(self._api_path(inbox_id, thread_id))
        return InboundThread(**response)

    def delete(self, inbox_id: int, thread_id: str) -> DeletedObject:
        """Delete a thread."""
        self._client.delete(self._api_path(inbox_id, thread_id))
        return DeletedObject(thread_id)

    def _api_path(self, inbox_id: int, thread_id: Optional[str] = None) -> str:
        path = f"/api/inbound/inboxes/{inbox_id}/threads"
        if thread_id:
            return f"{path}/{thread_id}"
        return path
