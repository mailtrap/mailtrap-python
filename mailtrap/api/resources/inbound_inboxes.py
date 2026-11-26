from mailtrap.http import HttpClient
from mailtrap.models.common import DeletedObject
from mailtrap.models.inbound import CreateInboundInboxParams
from mailtrap.models.inbound import InboundInbox
from mailtrap.models.inbound import UpdateInboundInboxParams


class InboundInboxesApi:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def get_list(self, folder_id: int) -> list[InboundInbox]:
        """Get all inboxes in an inbound folder."""
        response = self._client.get(self._api_path(folder_id))
        return [InboundInbox(**inbox) for inbox in response]

    def get_by_id(self, folder_id: int, inbox_id: int) -> InboundInbox:
        """Get an inbound inbox by ID."""
        response = self._client.get(self._api_path(folder_id, inbox_id))
        return InboundInbox(**response)

    def create(self, folder_id: int, params: CreateInboundInboxParams) -> InboundInbox:
        """Create a new inbound inbox in a folder."""
        response = self._client.post(self._api_path(folder_id), json=params.api_data)
        return InboundInbox(**response)

    def update(
        self, folder_id: int, inbox_id: int, params: UpdateInboundInboxParams
    ) -> InboundInbox:
        """Rename an inbound inbox."""
        response = self._client.patch(
            self._api_path(folder_id, inbox_id), json=params.api_data
        )
        return InboundInbox(**response)

    def delete(self, folder_id: int, inbox_id: int) -> DeletedObject:
        """Delete an inbound inbox."""
        self._client.delete(self._api_path(folder_id, inbox_id))
        return DeletedObject(inbox_id)

    def _api_path(self, folder_id: int, inbox_id: int | None = None) -> str:
        path = f"/api/inbound/folders/{folder_id}/inboxes"
        if inbox_id:
            return f"{path}/{inbox_id}"
        return path
