from mailtrap.models.permissions import PermissionResourceParams


class TestPermissionResourceParams:
    def test_api_data_with_all_fields_should_return_complete_dict(self) -> None:
        params = PermissionResourceParams(
            resource_id="123", resource_type="inbox", access_level="admin", _destroy=True
        )

        api_data = params.api_data

        assert api_data == {
            "resource_id": "123",
            "resource_type": "inbox",
            "access_level": "admin",
            "_destroy": True,
        }

    def test_api_data_with_required_fields_only_should_return_minimal_dict(self) -> None:
        params = PermissionResourceParams(resource_id="456", resource_type="project")

        api_data = params.api_data

        assert api_data == {"resource_id": "456", "resource_type": "project"}
