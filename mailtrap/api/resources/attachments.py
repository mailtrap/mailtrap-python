from typing import Optional

from mailtrap._deprecation import renamed_kwargs
from mailtrap.http import HttpClient
from mailtrap.models.attachments import Attachment


class AttachmentsApi:
    def __init__(self, client: HttpClient, account_id: str) -> None:
        self._account_id = account_id
        self._client = client

    @renamed_kwargs(inbox_id="sandbox_id")
    def get_list(
        self,
        sandbox_id: int,
        message_id: int,
    ) -> list[Attachment]:
        """Lists attachments with their details and download paths."""
        response = self._client.get(self._api_path(sandbox_id, message_id))
        return [Attachment(**attachment) for attachment in response]

    @renamed_kwargs(inbox_id="sandbox_id")
    def get(
        self,
        sandbox_id: int,
        message_id: int,
        attachment_id: int,
    ) -> Attachment:
        """Get message single attachment by sandbox_id, message_id and attachment_id."""
        response = self._client.get(self._api_path(sandbox_id, message_id, attachment_id))
        return Attachment(**response)

    def _api_path(
        self,
        sandbox_id: int,
        message_id: int,
        attachment_id: Optional[int] = None,
    ) -> str:
        path = (
            f"/api/accounts/{self._account_id}"
            f"/inboxes/{sandbox_id}"
            f"/messages/{message_id}"
            "/attachments"
        )
        if attachment_id:
            return f"{path}/{attachment_id}"
        return path
