from mailtrap.http import HttpClient
from mailtrap.models.permissions import PermissionResource
from mailtrap.models.permissions import PermissionResourceParams
from mailtrap.models.permissions import UpdatePermissionsResponse


class PermissionsApi:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def get_resources(self, account_id: int) -> list[PermissionResource]:
        """
        Get all resources in your account (Inboxes, Projects, Domains,
        Email Campaigns, Billing and Account itself) to which the token
        has admin access.
        """
        response = self._client.get(f"/api/accounts/{account_id}/permissions/resources")
        return [PermissionResource(**resource) for resource in response]

    def bulk_permissions_update(
        self,
        account_id: int,
        account_access_id: int,
        permissions: list[PermissionResourceParams],
    ) -> UpdatePermissionsResponse:
        """
        Manage user or token permissions. For this endpoint, you should send
        an array of objects (in JSON format) as the body of the request.
        If you send a combination of resource_type and resource_id that already exists,
        the permission is updated. If the combination doesn't exist,
        the permission is created.
        """
        response = self._client.put(
            f"/api/accounts/{account_id}"
            f"/account_accesses/{account_access_id}"
            "/permissions/bulk",
            json={"permissions": [resource.api_data for resource in permissions]},
        )
        return UpdatePermissionsResponse(**response)
