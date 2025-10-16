import pytest

from mailtrap.models.contacts import ContactEventParams
from mailtrap.models.contacts import ContactExportFilter
from mailtrap.models.contacts import ContactListParams
from mailtrap.models.contacts import CreateContactExportParams
from mailtrap.models.contacts import CreateContactFieldParams
from mailtrap.models.contacts import CreateContactParams
from mailtrap.models.contacts import ImportContactParams
from mailtrap.models.contacts import UpdateContactFieldParams
from mailtrap.models.contacts import UpdateContactParams


class TestCreateContactFieldParams:
    def test_create_contact_field_params_api_data_should_return_correct_dict(
        self,
    ) -> None:
        params = CreateContactFieldParams(
            name="Test Field", data_type="integer", merge_tag="test_field"
        )

        api_data = params.api_data

        assert api_data == {
            "name": "Test Field",
            "data_type": "integer",
            "merge_tag": "test_field",
        }


class TestUpdateContactFieldParams:
    def test_update_contact_field_params_with_none_values_should_raise_error(
        self,
    ) -> None:
        with pytest.raises(
            ValueError, match="At least one field must be provided for update action"
        ):
            _ = UpdateContactFieldParams()

    def test_update_contact_field_params_with_partial_values_should_not_raise_error(
        self,
    ) -> None:
        params = UpdateContactFieldParams(name="Updated Field")
        assert params.name == "Updated Field"
        assert params.merge_tag is None

    def test_update_contact_field_params_api_data_should_exclude_none_values(
        self,
    ) -> None:
        params = UpdateContactFieldParams(name="Updated Field")
        api_data = params.api_data

        assert api_data == {"name": "Updated Field"}

    def test_update_contact_field_params_api_data_with_all_values(self) -> None:
        params = UpdateContactFieldParams(name="Updated Field", merge_tag="updated_field")
        api_data = params.api_data

        assert api_data == {"name": "Updated Field", "merge_tag": "updated_field"}


class TestContactListParams:
    def test_create_contact_field_params_api_data_should_return_correct_dict(
        self,
    ) -> None:
        params = ContactListParams(name="Test List")
        api_data = params.api_data
        assert api_data == {"name": "Test List"}


class TestCreateContactParams:
    def test_create_contact_params_api_data_should_exclude_none_values(
        self,
    ) -> None:
        params = CreateContactParams(email="test@test.com")
        api_data = params.api_data
        assert api_data == {"email": "test@test.com"}

    def test_create_contact_params_api_data_should_return_correct_dicts(
        self,
    ) -> None:
        params = CreateContactParams(
            email="test@test.com", fields={"first_name": "Test"}, list_ids=[1]
        )
        api_data = params.api_data
        assert api_data == {
            "email": "test@test.com",
            "fields": {"first_name": "Test"},
            "list_ids": [1],
        }


class TestUpdateContactParams:
    def test_update_contact_params_with_none_values_should_raise_error(
        self,
    ) -> None:
        with pytest.raises(
            ValueError, match="At least one field must be provided for update action"
        ):
            _ = UpdateContactParams()

    def test_update_contact_params_api_data_should_exclude_none_values(
        self,
    ) -> None:
        params = UpdateContactParams(email="test@test.com")
        api_data = params.api_data
        assert api_data == {"email": "test@test.com"}

    def test_update_contact_params_api_data_should_return_correct_dicts(
        self,
    ) -> None:
        params = UpdateContactParams(
            email="test@test.com",
            fields={"first_name": "Test"},
            list_ids_included=[2],
            list_ids_excluded=[1],
            unsubscribed=False,
        )
        api_data = params.api_data
        assert api_data == {
            "email": "test@test.com",
            "fields": {"first_name": "Test"},
            "list_ids_included": [2],
            "list_ids_excluded": [1],
            "unsubscribed": False,
        }


class TestImportContactParams:
    def test_import_contact_params_api_data_should_exclude_none_values(
        self,
    ) -> None:
        params = ImportContactParams(email="test@test.com")
        api_data = params.api_data
        assert api_data == {"email": "test@test.com"}

    def test_import_contact_params_api_data_should_return_correct_dicts(
        self,
    ) -> None:
        params = ImportContactParams(
            email="test@test.com",
            fields={"first_name": "Test"},
            list_ids_included=[1],
            list_ids_excluded=[2],
        )
        api_data = params.api_data
        assert api_data == {
            "email": "test@test.com",
            "fields": {"first_name": "Test"},
            "list_ids_included": [1],
            "list_ids_excluded": [2],
        }


class TestContactExportFilter:
    def test_contact_export_filter_api_data_should_return_correct_dict(self) -> None:
        """Test that ContactExportFilter api_data returns correct dictionary."""
        filter_obj = ContactExportFilter(name="list_id", operator="in", value=[1, 2, 3])

        api_data = filter_obj.api_data

        assert api_data == {"name": "list_id", "operator": "in", "value": [1, 2, 3]}


class TestCreateContactExportParams:
    def test_create_contact_export_params_api_data_should_return_correct_dict(
        self,
    ) -> None:
        """Test that CreateContactExportParams api_data returns correct dictionary."""
        params = CreateContactExportParams(
            filters=[ContactExportFilter(name="list_id", operator="in", value=[1, 2, 3])]
        )

        api_data = params.api_data

        assert api_data == {
            "filters": [{"name": "list_id", "operator": "in", "value": [1, 2, 3]}]
        }

    def test_create_contact_export_params_with_multiple_filters_should_work(self) -> None:
        """Test that multiple filters work correctly."""
        params = CreateContactExportParams(
            filters=[
                ContactExportFilter(name="list_id", operator="in", value=[1, 2, 3]),
                ContactExportFilter(name="field_id", operator="equal", value=[4, 5, 6]),
            ]
        )

        api_data = params.api_data

        assert len(api_data["filters"]) == 2
        assert api_data["filters"][0]["name"] == "list_id"
        assert api_data["filters"][1]["name"] == "field_id"

    def test_create_contact_export_params_with_empty_filters_should_work(self) -> None:
        """Test that empty filters list works correctly."""
        params = CreateContactExportParams(filters=[])

        api_data = params.api_data

        assert api_data == {"filters": []}


class TestContactEventParams:
    def test_contact_event_params_api_data_should_return_correct_dict(
        self,
    ) -> None:
        params = ContactEventParams(
            name="UserLogin",
            params={
                "user_id": 101,
                "user_name": "John Smith",
                "is_active": True,
                "last_seen": None,
            },
        )

        api_data = params.api_data
        assert api_data == {
            "name": "UserLogin",
            "params": {
                "user_id": 101,
                "user_name": "John Smith",
                "is_active": True,
                "last_seen": None,
            },
        }

    def test_contact_event_params_with_empty_params_should_work(self) -> None:
        """Test that ContactEventParams works correctly when params are omitted."""
        params = ContactEventParams(name="UserLogin")
        api_data = params.api_data
        assert api_data == {"name": "UserLogin"}
