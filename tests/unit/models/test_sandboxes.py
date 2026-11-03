import pytest

from mailtrap.models.sandboxes import CreateSandboxParams
from mailtrap.models.sandboxes import UpdateSandboxParams


class TestCreateSandboxParams:
    def test_api_data_should_return_dict_with_all_props(self) -> None:
        entity = CreateSandboxParams(name="test")
        assert entity.api_data == {"name": "test"}


class TestUpdateSandboxParams:
    def test_raise_error_when_all_fields_are_missing(self) -> None:
        with pytest.raises(
            ValueError, match="At least one field must be provided for update action"
        ):
            _ = UpdateSandboxParams()

    def test_api_data_should_return_dict_with_all_props(self) -> None:
        entity = UpdateSandboxParams(name="test", email_username="test_username")
        assert entity.api_data == {"name": "test", "email_username": "test_username"}

    def test_api_data_should_return_dict_with_required_props_only(self) -> None:
        entity = UpdateSandboxParams(name="test")
        assert entity.api_data == {"name": "test"}

        entity = UpdateSandboxParams(email_username="test_username")
        assert entity.api_data == {"email_username": "test_username"}
