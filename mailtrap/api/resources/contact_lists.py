from typing import Optional

from mailtrap.http import HttpClient
from mailtrap.models.common import DeletedObject
from mailtrap.models.contacts import ContactList
from mailtrap.models.contacts import ContactListParams
from mailtrap.models.contacts import ContactListsFilterParams


class ContactListsApi:
    def __init__(self, client: HttpClient, account_id: str) -> None:
        self._account_id = account_id
        self._client = client

    def get_list(self, search: Optional[str] = None) -> list[ContactList]:
        """
        Get all contact lists existing in your account.

        :param search: Optionally filter lists by name
            (case-insensitive prefix match).
        """
        params = ContactListsFilterParams(search=search)
        response = self._client.get(self._api_path(), params=params.api_query_params)
        return [ContactList(**field) for field in response]

    def get_by_id(self, list_id: int) -> ContactList:
        """Get a contact list by ID."""
        response = self._client.get(self._api_path(list_id))
        return ContactList(**response)

    def create(self, list_params: ContactListParams) -> ContactList:
        """Create new Contact Lists."""
        response = self._client.post(
            self._api_path(),
            json=list_params.api_data,
        )
        return ContactList(**response)

    def update(self, list_id: int, list_params: ContactListParams) -> ContactList:
        """Update existing Contact List."""
        response = self._client.patch(
            self._api_path(list_id),
            json=list_params.api_data,
        )
        return ContactList(**response)

    def delete(self, list_id: int) -> DeletedObject:
        """Delete existing Contact List."""
        self._client.delete(self._api_path(list_id))
        return DeletedObject(list_id)

    def _api_path(self, list_id: Optional[int] = None) -> str:
        path = f"/api/accounts/{self._account_id}/contacts/lists"
        if list_id is not None:
            return f"{path}/{list_id}"
        return path
