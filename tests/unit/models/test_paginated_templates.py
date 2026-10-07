import pytest

from mailtrap.models.paginated_templates import CreateTemplateParams
from mailtrap.models.paginated_templates import TemplateListParams
from mailtrap.models.paginated_templates import UpdateTemplateParams


class TestTemplateListParams:
    def test_api_query_params_should_drop_unset_fields(self) -> None:
        assert TemplateListParams(per_page=10).api_query_params == {"per_page": 10}

    def test_api_query_params_should_include_all_fields(self) -> None:
        params = TemplateListParams(per_page=10, token=2)
        assert params.api_query_params == {"per_page": 10, "token": 2}


class TestCreateTemplateParams:
    def test_api_data_should_return_dict_with_required_props_only(self) -> None:
        entity = CreateTemplateParams(name="test", subject="test", category="test")
        assert entity.api_data == {
            "name": "test",
            "subject": "test",
            "category": "test",
        }

    def test_api_data_should_return_dict_with_all_props(self) -> None:
        entity = CreateTemplateParams(
            name="test",
            subject="test",
            category="test",
            body_html="<p>test</p>",
            body_text="test",
        )
        assert entity.api_data == {
            "name": "test",
            "subject": "test",
            "category": "test",
            "body_html": "<p>test</p>",
            "body_text": "test",
        }


class TestUpdateTemplateParams:
    def test_raise_error_when_all_fields_are_missing(self) -> None:
        with pytest.raises(ValueError) as exc:
            _ = UpdateTemplateParams()

        assert "At least one field must be provided for update action" in str(exc)

    def test_api_data_should_return_only_provided_props(self) -> None:
        entity = UpdateTemplateParams(name="test", body_text="text")
        assert entity.api_data == {"name": "test", "body_text": "text"}
