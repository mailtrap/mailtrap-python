from typing import Optional

from mailtrap.http import HttpClient
from mailtrap.models.contacts import ContactEvent
from mailtrap.models.contacts import ContactEventParams


class ContactEventsApi:
    def __init__(self, client: HttpClient, account_id: str) -> None:
        self._account_id = account_id
        self._client = client

    def create(
        self,
        contact_identifier: str,
        contact_event_params: ContactEventParams,
    ) -> ContactEvent:
        """Create a new Contact Event"""
        response = self._client.post(
            self._api_path(contact_identifier),
            json=contact_event_params.api_data,
        )
        return ContactEvent(**response)

    def _api_path(self, contact_identifier: Optional[str] = None) -> str:
        return f"/api/accounts/{self._account_id}/contacts/{contact_identifier}/events"
