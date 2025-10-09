from typing import Optional

from mailtrap.http import HttpClient
from mailtrap.models.contacts import ContactExportDetail
from mailtrap.models.contacts import CreateContactExportParams


class ContactExportsApi:
    def __init__(self, client: HttpClient, account_id: str) -> None:
        self._account_id = account_id
        self._client = client

    def create(
        self, contact_exports_params: CreateContactExportParams
    ) -> ContactExportDetail:
        """Create a new Contact Export"""
        response = self._client.post(
            self._api_path(),
            json=contact_exports_params.api_data,
        )
        return ContactExportDetail(**response)

    def get_by_id(self, export_id: int) -> ContactExportDetail:
        """Get Contact Export"""
        response = self._client.get(self._api_path(export_id))
        return ContactExportDetail(**response)

    def _api_path(self, export_id: Optional[int] = None) -> str:
        path = f"/api/accounts/{self._account_id}/contacts/exports"
        if export_id is not None:
            return f"{path}/{export_id}"
        return path
