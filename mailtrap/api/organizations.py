from mailtrap.api.resources.sub_accounts import SubAccountsApi
from mailtrap.http import HttpClient


class OrganizationsBaseApi:
    def __init__(self, client: HttpClient, organization_id: str) -> None:
        self._organization_id = organization_id
        self._client = client

    @property
    def sub_accounts(self) -> SubAccountsApi:
        return SubAccountsApi(organization_id=self._organization_id, client=self._client)
