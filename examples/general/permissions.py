import mailtrap as mt
from mailtrap.models.permissions import PermissionResource
from mailtrap.models.permissions import UpdatePermissionsResponse

API_TOKEN = "YOUR_API_TOKEN"
ACCOUNT_ID = "YOUR_ACCOUNT_ID"

client = mt.MailtrapClient(token=API_TOKEN)
permissions_api = client.general_api.permissions


def get_permission_resources(account_id: int) -> list[PermissionResource]:
    return permissions_api.get_resources(account_id=account_id)


def bulk_permissions_update(
    account_id: int,
    account_access_id: int,
    permissions: list[mt.PermissionResourceParams],
) -> UpdatePermissionsResponse:
    return permissions_api.bulk_permissions_update(
        account_id=account_id,
        account_access_id=account_access_id,
        permissions=permissions,
    )


if __name__ == "__main__":
    resources = get_permission_resources(ACCOUNT_ID)
    print(resources)
    if resources:
        account_access_id = resources[0].id
        permissions = [
            mt.PermissionResourceParams(
                resource_id=resources[0].id,
                resource_type=resources[0].type,
                access_level="viewer",
            )
        ]
        updated = bulk_permissions_update(
            ACCOUNT_ID,
            account_access_id,
            permissions,
        )
        print(updated)
