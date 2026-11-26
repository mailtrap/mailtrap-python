from mailtrap.http import HttpClient
from mailtrap.models.common import DeletedObject
from mailtrap.models.inbound import CreateInboundFolderParams
from mailtrap.models.inbound import InboundFolder
from mailtrap.models.inbound import UpdateInboundFolderParams


class InboundFoldersApi:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def get_list(self) -> list[InboundFolder]:
        """Get all inbound folders in the account."""
        response = self._client.get(self._api_path())
        return [InboundFolder(**folder) for folder in response]

    def get_by_id(self, folder_id: int) -> InboundFolder:
        """Get an inbound folder by ID."""
        response = self._client.get(self._api_path(folder_id))
        return InboundFolder(**response)

    def create(self, params: CreateInboundFolderParams) -> InboundFolder:
        """Create a new inbound folder."""
        response = self._client.post(self._api_path(), json=params.api_data)
        return InboundFolder(**response)

    def update(self, folder_id: int, params: UpdateInboundFolderParams) -> InboundFolder:
        """Rename an inbound folder."""
        response = self._client.patch(self._api_path(folder_id), json=params.api_data)
        return InboundFolder(**response)

    def delete(self, folder_id: int) -> DeletedObject:
        """Delete an inbound folder along with all of its inboxes."""
        self._client.delete(self._api_path(folder_id))
        return DeletedObject(folder_id)

    def _api_path(self, folder_id: int | None = None) -> str:
        path = "/api/inbound/folders"
        if folder_id:
            return f"{path}/{folder_id}"
        return path
