from typing import Optional

from mailtrap.http import HttpClient
from mailtrap.models.suppressions import CreateSuppressionParams
from mailtrap.models.suppressions import Suppression
from mailtrap.models.suppressions import SuppressionResponse


class SuppressionsApi:
    def __init__(self, client: HttpClient, account_id: str) -> None:
        self._account_id = account_id
        self._client = client

    def get_list(
        self, email: Optional[str] = None, include_topic_unsubscriptions: bool = False
    ) -> list[Suppression]:
        """
        List and search suppressions by email.
        The endpoint returns up to 1000 suppressions per request.
        With `include_topic_unsubscriptions`, the list also has the contacts'
        unsubscribes from single subscription topics, of type
        "topic unsubscription".
        """
        params: dict[str, str] = {}
        if email is not None:
            params["email"] = email
        if include_topic_unsubscriptions:
            # The API opts in on the exact string "true"; requests would send "True".
            params["include_topic_unsubscriptions"] = "true"
        response = self._client.get(self._api_path(), params=params or None)
        return [Suppression(**suppression) for suppression in response]

    def create(self, params: CreateSuppressionParams) -> Suppression:
        """
        Add an email address to the account's suppression list. `type` defaults
        to "manual import" when omitted.
        """
        response = self._client.post(self._api_path(), json=params.api_data)
        return SuppressionResponse(**response).data

    def delete(self, suppression_id: str) -> Suppression:
        """
        Delete a suppression by ID. Mailtrap will no longer prevent
        sending to this email unless it's recorded in suppressions again.
        A "topic unsubscription" can't be deleted: the API returns 404.
        """
        response = self._client.delete(self._api_path(suppression_id))
        return Suppression(**response)

    def _api_path(self, suppression_id: Optional[str] = None) -> str:
        path = f"/api/accounts/{self._account_id}/suppressions"
        if suppression_id is not None:
            return f"{path}/{suppression_id}"
        return path
