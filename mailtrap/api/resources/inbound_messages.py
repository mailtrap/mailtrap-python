from typing import Any

from mailtrap.http import HttpClient
from mailtrap.models.common import DeletedObject
from mailtrap.models.inbound import ForwardInboundMessageParams
from mailtrap.models.inbound import InboundMessageDetails
from mailtrap.models.inbound import InboundMessagesListResponse
from mailtrap.models.inbound import InboundSendResult
from mailtrap.models.inbound import ReplyInboundMessageParams


class InboundMessagesApi:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def get_list(
        self, inbox_id: int, last_id: str | None = None
    ) -> InboundMessagesListResponse:
        """
        List received messages in an inbox. Pass last_id from a previous
        response to fetch the next page.
        """
        params: dict[str, Any] = {}
        if last_id:
            params["last_id"] = last_id
        response = self._client.get(self._api_path(inbox_id), params=params or None)
        return InboundMessagesListResponse(**response)

    def get_by_id(self, inbox_id: int, message_id: str) -> InboundMessageDetails:
        """Get a single message with its body and attachment download URLs."""
        response = self._client.get(self._api_path(inbox_id, message_id))
        return InboundMessageDetails(**response)

    def delete(self, inbox_id: int, message_id: str) -> DeletedObject:
        """Delete a message."""
        self._client.delete(self._api_path(inbox_id, message_id))
        return DeletedObject(message_id)

    def reply(
        self, inbox_id: int, message_id: str, params: ReplyInboundMessageParams
    ) -> InboundSendResult:
        """Reply to a message (to the original sender). Sends a real email."""
        response = self._client.post(
            f"{self._api_path(inbox_id, message_id)}/reply", json=params.api_data
        )
        return InboundSendResult(**response)

    def reply_all(
        self, inbox_id: int, message_id: str, params: ReplyInboundMessageParams
    ) -> InboundSendResult:
        """Reply to a message and copy its other recipients. Sends a real email."""
        response = self._client.post(
            f"{self._api_path(inbox_id, message_id)}/reply_all", json=params.api_data
        )
        return InboundSendResult(**response)

    def forward(
        self, inbox_id: int, message_id: str, params: ForwardInboundMessageParams
    ) -> InboundSendResult:
        """Forward a message to new recipients. Sends a real email."""
        response = self._client.post(
            f"{self._api_path(inbox_id, message_id)}/forward", json=params.api_data
        )
        return InboundSendResult(**response)

    def _api_path(self, inbox_id: int, message_id: str | None = None) -> str:
        path = f"/api/inbound/inboxes/{inbox_id}/messages"
        if message_id:
            return f"{path}/{message_id}"
        return path
