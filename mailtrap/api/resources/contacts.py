from urllib.parse import quote

from mailtrap.http import HttpClient
from mailtrap.models.common import DeletedObject
from mailtrap.models.contacts import Contact
from mailtrap.models.contacts import ContactResponse
from mailtrap.models.contacts import CreateContactParams
from mailtrap.models.contacts import UpdateContactParams


class ContactsApi:
    def __init__(self, client: HttpClient, account_id: str) -> None:
        self._account_id = account_id
        self._client = client

    def get_by_id(self, contact_id_or_email: str) -> Contact:
        """Get contact using id or email (URL encoded)."""
        response = self._client.get(self._api_path(contact_id_or_email))
        return ContactResponse(**response).data

    def create(self, contact_params: CreateContactParams) -> Contact:
        """Create a new contact."""
        response = self._client.post(
            self._api_path(),
            json={"contact": contact_params.api_data},
        )
        return ContactResponse(**response).data

    def update(
        self, contact_id_or_email: str, contact_params: UpdateContactParams
    ) -> Contact:
        """Update contact using id or email (URL encoded)."""
        response = self._client.patch(
            self._api_path(contact_id_or_email),
            json={"contact": contact_params.api_data},
        )
        return ContactResponse(**response).data

    def delete(self, contact_id_or_email: str) -> DeletedObject:
        """Delete contact using id or email (URL encoded)."""
        self._client.delete(self._api_path(contact_id_or_email))
        return DeletedObject(contact_id_or_email)

    def _api_path(self, contact_id_or_email: str | None = None) -> str:
        path = f"/api/accounts/{self._account_id}/contacts"
        if contact_id_or_email is not None:
            return f"{path}/{quote(contact_id_or_email, safe='')}"
        return path
