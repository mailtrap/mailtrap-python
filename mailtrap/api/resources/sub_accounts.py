from mailtrap.http import HttpClient
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

    def _api_path(self) -> str:
        return f"/api/organizations/{self._organization_id}/sub_accounts"
