import json
from typing import Any
from urllib.parse import parse_qs
from urllib.parse import urlparse

import pytest
import responses

from mailtrap.api.resources.account_templates import AccountTemplatesApi
from mailtrap.config import GENERAL_HOST
from mailtrap.exceptions import APIError
from mailtrap.http import HttpClient
from mailtrap.models.account_templates import CreateTemplateParams
from mailtrap.models.account_templates import Template
from mailtrap.models.account_templates import TemplateListParams
from mailtrap.models.account_templates import TemplateListResponse
from mailtrap.models.account_templates import UpdateTemplateParams
from mailtrap.models.common import DeletedObject
from tests import conftest

ACCOUNT_ID = "321"
TEMPLATE_ID = 26730
BASE_TEMPLATES_URL = f"https://{GENERAL_HOST}/api/accounts/{ACCOUNT_ID}/templates"


@pytest.fixture
def client() -> AccountTemplatesApi:
    return AccountTemplatesApi(account_id=ACCOUNT_ID, client=HttpClient(GENERAL_HOST))


@pytest.fixture
def sample_template_dict() -> dict[str, Any]:
    return {
        "id": TEMPLATE_ID,
        "uuid": "b81aabcd-1a1e-41cf-91b6-eca0254b3d96",
        "name": "Promotion Template",
        "category": "Promotion",
        "subject": "Promotion Template subject",
        "body_html": "<div>body</div>",
        "body_text": "Text body",
        "created_at": "2026-05-01T10:15:00.000Z",
        "updated_at": "2026-05-02T09:00:00.000Z",
    }


class TestAccountTemplatesApi:

    @pytest.mark.parametrize(
        "status_code,response_json,expected_error_message",
        [
            (
                conftest.UNAUTHORIZED_STATUS_CODE,
                conftest.UNAUTHORIZED_RESPONSE,
                conftest.UNAUTHORIZED_ERROR_MESSAGE,
            ),
            (
                conftest.RATE_LIMIT_ERROR_STATUS_CODE,
                conftest.RATE_LIMIT_ERROR_RESPONSE,
                conftest.RATE_LIMIT_ERROR_MESSAGE,
            ),
            (
                conftest.VALIDATION_ERRORS_STATUS_CODE,
                {"errors": "token is out of range"},
                "token is out of range",
            ),
        ],
    )
    @responses.activate
    def test_get_list_should_raise_api_errors(
        self,
        client: AccountTemplatesApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.get(BASE_TEMPLATES_URL, status=status_code, json=response_json)

        with pytest.raises(APIError) as exc_info:
            client.get_list()

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_list_should_return_templates_and_pagination(
        self, client: AccountTemplatesApi, sample_template_dict: dict
    ) -> None:
        responses.get(
            BASE_TEMPLATES_URL,
            json={
                "data": [sample_template_dict, {"id": 26731, "name": "Second"}],
                "pagination": {
                    "token": 1,
                    "prev_token": None,
                    "next_token": 2,
                    "first_url": f"{BASE_TEMPLATES_URL}?per_page=50&token=1",
                    "prev_url": None,
                    "current_url": f"{BASE_TEMPLATES_URL}?per_page=50&token=1",
                    "next_url": f"{BASE_TEMPLATES_URL}?per_page=50&token=2",
                },
            },
            status=200,
        )

        result = client.get_list()

        assert isinstance(result, TemplateListResponse)
        assert all(isinstance(t, Template) for t in result.data)
        assert len(result.data) == 2
        assert result.data[0].id == TEMPLATE_ID
        assert result.data[0].uuid == "b81aabcd-1a1e-41cf-91b6-eca0254b3d96"
        assert result.data[0].body_html == "<div>body</div>"
        assert result.data[1].name == "Second"
        assert result.data[1].body_html is None
        assert result.pagination is not None
        assert result.pagination.token == 1
        assert result.pagination.prev_token is None
        assert result.pagination.next_token == 2
        assert result.pagination.next_url == f"{BASE_TEMPLATES_URL}?per_page=50&token=2"

    @responses.activate
    def test_get_list_should_return_empty_list(
        self, client: AccountTemplatesApi
    ) -> None:
        responses.get(
            BASE_TEMPLATES_URL, json={"data": [], "pagination": {"token": 1}}, status=200
        )

        result = client.get_list()

        assert isinstance(result, TemplateListResponse)
        assert result.data == []

    @responses.activate
    def test_get_list_should_send_per_page_and_token_query_params(
        self, client: AccountTemplatesApi
    ) -> None:
        responses.get(BASE_TEMPLATES_URL, json={"data": [], "pagination": {}}, status=200)

        client.get_list(TemplateListParams(per_page=25, token=2))

        query = parse_qs(urlparse(responses.calls[0].request.url).query)
        assert query["per_page"] == ["25"]
        assert query["token"] == ["2"]

    @responses.activate
    def test_get_list_should_send_no_query_params_by_default(
        self, client: AccountTemplatesApi
    ) -> None:
        responses.get(BASE_TEMPLATES_URL, json={"data": [], "pagination": {}}, status=200)

        client.get_list()

        assert urlparse(responses.calls[0].request.url).query == ""

    @pytest.mark.parametrize(
        "status_code,response_json,expected_error_message",
        [
            (
                conftest.UNAUTHORIZED_STATUS_CODE,
                conftest.UNAUTHORIZED_RESPONSE,
                conftest.UNAUTHORIZED_ERROR_MESSAGE,
            ),
            (
                conftest.NOT_FOUND_STATUS_CODE,
                conftest.NOT_FOUND_RESPONSE,
                conftest.NOT_FOUND_ERROR_MESSAGE,
            ),
        ],
    )
    @responses.activate
    def test_get_by_id_should_raise_api_errors(
        self,
        client: AccountTemplatesApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.get(
            f"{BASE_TEMPLATES_URL}/{TEMPLATE_ID}",
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.get_by_id(TEMPLATE_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_by_id_should_unwrap_data_envelope(
        self, client: AccountTemplatesApi, sample_template_dict: dict
    ) -> None:
        responses.get(
            f"{BASE_TEMPLATES_URL}/{TEMPLATE_ID}",
            json={"data": sample_template_dict},
            status=200,
        )

        template = client.get_by_id(TEMPLATE_ID)

        assert isinstance(template, Template)
        assert template.id == TEMPLATE_ID
        assert template.name == "Promotion Template"
        assert template.category == "Promotion"
        assert template.subject == "Promotion Template subject"
        assert template.body_text == "Text body"
        assert template.created_at == "2026-05-01T10:15:00.000Z"

    @pytest.mark.parametrize(
        "status_code,response_json,expected_error_message",
        [
            (
                conftest.UNAUTHORIZED_STATUS_CODE,
                conftest.UNAUTHORIZED_RESPONSE,
                conftest.UNAUTHORIZED_ERROR_MESSAGE,
            ),
            (
                conftest.VALIDATION_ERRORS_STATUS_CODE,
                {"errors": {"name": ["can't be blank"]}},
                "name: can't be blank",
            ),
        ],
    )
    @responses.activate
    def test_create_should_raise_api_errors(
        self,
        client: AccountTemplatesApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.post(BASE_TEMPLATES_URL, status=status_code, json=response_json)

        with pytest.raises(APIError) as exc_info:
            client.create(CreateTemplateParams(name="", subject="s", category="c"))

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_create_should_send_flat_body_and_unwrap_response(
        self, client: AccountTemplatesApi, sample_template_dict: dict
    ) -> None:
        responses.post(
            BASE_TEMPLATES_URL, json={"data": sample_template_dict}, status=201
        )

        template = client.create(
            CreateTemplateParams(
                name="Promotion Template",
                subject="Promotion Template subject",
                category="Promotion",
                body_html="<div>body</div>",
            )
        )

        assert isinstance(template, Template)
        assert template.id == TEMPLATE_ID
        assert json.loads(responses.calls[0].request.body) == {
            "name": "Promotion Template",
            "subject": "Promotion Template subject",
            "category": "Promotion",
            "body_html": "<div>body</div>",
        }

    @pytest.mark.parametrize(
        "status_code,response_json,expected_error_message",
        [
            (
                conftest.UNAUTHORIZED_STATUS_CODE,
                conftest.UNAUTHORIZED_RESPONSE,
                conftest.UNAUTHORIZED_ERROR_MESSAGE,
            ),
            (
                conftest.NOT_FOUND_STATUS_CODE,
                conftest.NOT_FOUND_RESPONSE,
                conftest.NOT_FOUND_ERROR_MESSAGE,
            ),
            (
                conftest.VALIDATION_ERRORS_STATUS_CODE,
                {"errors": {"subject": ["can't be blank"]}},
                "subject: can't be blank",
            ),
        ],
    )
    @responses.activate
    def test_update_should_raise_api_errors(
        self,
        client: AccountTemplatesApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.patch(
            f"{BASE_TEMPLATES_URL}/{TEMPLATE_ID}",
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.update(TEMPLATE_ID, UpdateTemplateParams(subject=""))

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_update_should_patch_flat_body_and_unwrap_response(
        self, client: AccountTemplatesApi, sample_template_dict: dict
    ) -> None:
        responses.patch(
            f"{BASE_TEMPLATES_URL}/{TEMPLATE_ID}",
            json={"data": {**sample_template_dict, "name": "Renamed"}},
            status=200,
        )

        template = client.update(TEMPLATE_ID, UpdateTemplateParams(name="Renamed"))

        assert isinstance(template, Template)
        assert template.name == "Renamed"
        assert json.loads(responses.calls[0].request.body) == {"name": "Renamed"}

    @pytest.mark.parametrize(
        "status_code,response_json,expected_error_message",
        [
            (
                conftest.UNAUTHORIZED_STATUS_CODE,
                conftest.UNAUTHORIZED_RESPONSE,
                conftest.UNAUTHORIZED_ERROR_MESSAGE,
            ),
            (
                conftest.NOT_FOUND_STATUS_CODE,
                conftest.NOT_FOUND_RESPONSE,
                conftest.NOT_FOUND_ERROR_MESSAGE,
            ),
        ],
    )
    @responses.activate
    def test_delete_should_raise_api_errors(
        self,
        client: AccountTemplatesApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.delete(
            f"{BASE_TEMPLATES_URL}/{TEMPLATE_ID}",
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.delete(TEMPLATE_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_delete_should_return_deleted_object(
        self, client: AccountTemplatesApi
    ) -> None:
        responses.delete(f"{BASE_TEMPLATES_URL}/{TEMPLATE_ID}", status=204)

        result = client.delete(TEMPLATE_ID)

        assert isinstance(result, DeletedObject)
        assert result.id == TEMPLATE_ID
