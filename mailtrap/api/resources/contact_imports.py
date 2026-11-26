from mailtrap.http import HttpClient
from mailtrap.models.contacts import ContactImport
from mailtrap.models.contacts import ImportContactParams


class ContactImportsApi:
    def __init__(self, client: HttpClient, account_id: str) -> None:
        self._account_id = account_id
        self._client = client

    def import_contacts(self, contacts: list[ImportContactParams]) -> ContactImport:
        """
        Import contacts in bulk with support for custom fields and list management.
        Existing contacts with matching email addresses will be updated automatically.
        You can import up to 50,000 contacts per request. The import process runs
        asynchronously - use the returned import ID to check the status and results.
        """
        response = self._client.post(
            self._api_path(),
            json={"contacts": [contact.api_data for contact in contacts]},
        )
        return ContactImport(**response)

    def get_by_id(self, import_id: int) -> ContactImport:
        """Get Contact Import by ID."""
        response = self._client.get(self._api_path(import_id))
        return ContactImport(**response)

    def _api_path(self, import_id: int | None = None) -> str:
        path = f"/api/accounts/{self._account_id}/contacts/imports"
        if import_id is not None:
            return f"{path}/{import_id}"
        return path
