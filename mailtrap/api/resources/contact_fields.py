from mailtrap.http import HttpClient
from mailtrap.models.common import DeletedObject
from mailtrap.models.contacts import ContactField
from mailtrap.models.contacts import CreateContactFieldParams
from mailtrap.models.contacts import UpdateContactFieldParams


class ContactFieldsApi:
    def __init__(self, client: HttpClient, account_id: str) -> None:
        self._account_id = account_id
        self._client = client

    def get_list(self) -> list[ContactField]:
        """Get all Contact Fields existing in your account."""
        response = self._client.get(self._api_path())
        return [ContactField(**field) for field in response]

    def get_by_id(self, field_id: int) -> ContactField:
        """Get a contact Field by ID."""
        response = self._client.get(
            self._api_path(field_id),
        )
        return ContactField(**response)

    def create(self, field_params: CreateContactFieldParams) -> ContactField:
        """Create new Contact Fields. Please note, you can have up to 40 fields."""
        response = self._client.post(
            self._api_path(),
            json=field_params.api_data,
        )
        return ContactField(**response)

    def update(
        self, field_id: int, field_params: UpdateContactFieldParams
    ) -> ContactField:
        """
        Update existing Contact Field. Please note,
        you cannot change data_type of the field.
        """
        response = self._client.patch(
            self._api_path(field_id),
            json=field_params.api_data,
        )
        return ContactField(**response)

    def delete(self, field_id: int) -> DeletedObject:
        """
        Delete existing Contact Field Please, note, you cannot delete a Contact Field
        which is used in Automations, Email Campaigns (started or scheduled), and in
        conditions of Contact Segments (you'll see the corresponding error)
        """
        self._client.delete(self._api_path(field_id))
        return DeletedObject(field_id)

    def _api_path(self, field_id: int | None = None) -> str:
        path = f"/api/accounts/{self._account_id}/contacts/fields"
        if field_id is not None:
            return f"{path}/{field_id}"
        return path
