from mailtrap.api.resources.account_accesses import AccountAccessesApi
from mailtrap.api.resources.accounts import AccountsApi
from mailtrap.api.resources.billing import BillingApi
from mailtrap.api.resources.permissions import PermissionsApi
from mailtrap.http import HttpClient


class GeneralApi:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    @property
    def accounts(self) -> AccountsApi:
        return AccountsApi(client=self._client)

    @property
    def account_accesses(self) -> AccountAccessesApi:
        return AccountAccessesApi(client=self._client)

    @property
    def billing(self) -> BillingApi:
        return BillingApi(client=self._client)

    @property
    def permissions(self) -> PermissionsApi:
        return PermissionsApi(client=self._client)
