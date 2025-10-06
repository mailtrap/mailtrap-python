from typing import Optional
from urllib.parse import quote

from mailtrap.http import HttpClient
from mailtrap.models.accounts import AccountAccess
from mailtrap.models.accounts import AccountAccessFilterParams
from mailtrap.models.common import DeletedObject


class AccountAccessesApi:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def get_list(
        self, account_id: int, filter_params: Optional[AccountAccessFilterParams] = None
    ) -> list[AccountAccess]:
        """
        Get list of account accesses for which specifier_type is User or Invite.
        You have to have account admin/owner permissions for this endpoint to work.
        If you specify project_ids, inbox_ids or domain_ids, the endpoint will return
        account accesses for these resources.
        """
        response = self._client.get(
            self._api_path(account_id),
            params=filter_params.api_data if filter_params else None,
        )
        return [AccountAccess(**account_access) for account_access in response]

    def delete(self, account_id: int, account_access_id: int) -> DeletedObject:
        """
        If specifier type is User, it removes user permissions.
        If specifier type is Invite or ApiToken, it removes specifier
        along with permissions. You have to be an account admin/owner
        for this method to work.
        """
        self._client.delete(self._api_path(account_id, account_access_id))
        return DeletedObject(account_access_id)

    def _api_path(self, account_id: int, account_access_id: Optional[int] = None) -> str:
        path = f"/api/accounts/{account_id}/account_accesses"
        if account_access_id is not None:
            return f"{path}/{quote(str(account_access_id), safe='')}"
        return path
