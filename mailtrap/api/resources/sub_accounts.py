from typing import Optional

from mailtrap.http import HttpClient
from mailtrap.models.common import DeletedObject
from mailtrap.models.organizations import CreateSubAccountParams
from mailtrap.models.organizations import SubAccount


class SubAccountsApi:
    def __init__(self, client: HttpClient, organization_id: str) -> None:
        self._organization_id = organization_id
        self._client = client

    def get_list(self) -> list[SubAccount]:
        """
        Get a list of sub accounts for the organization. Requires sub
        account management permissions for this organization.
        """
        response = self._client.get(self._api_path())
        return [SubAccount(**sub_account) for sub_account in response]

    def create(self, sub_account_params: CreateSubAccountParams) -> SubAccount:
        """
        Create a new sub account under the organization. Requires sub
        account management permissions for this organization.
        """
        response = self._client.post(
            self._api_path(),
            json={"account": sub_account_params.api_data},
        )
        return SubAccount(**response)

    def delete(self, sub_account_id: int) -> DeletedObject:
        """
        Delete a sub account of the organization. Requires sub account
        management permissions for this organization.

        The sub account and all of its data are removed permanently and cannot
        be restored. Deleting the organization's last sub account also deletes
        the organization. A repeated call for the same sub account returns
        a 404 error.

        Rate limit: 10 requests per minute per organization.
        """
        self._client.delete(self._api_path(sub_account_id))
        return DeletedObject(id=sub_account_id)

    def _api_path(self, sub_account_id: Optional[int] = None) -> str:
        path = f"/api/organizations/{self._organization_id}/sub_accounts"
        if sub_account_id is not None:
            return f"{path}/{sub_account_id}"
        return path
