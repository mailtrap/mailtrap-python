from typing import Any

import pytest
import responses

from mailtrap.api.resources.projects import ProjectsApi
from mailtrap.config import GENERAL_HOST
from mailtrap.exceptions import APIError
from mailtrap.http import HttpClient
from mailtrap.models.common import DeletedObject
from mailtrap.models.projects import Project
from mailtrap.models.projects import ProjectParams
from tests import conftest

ACCOUNT_ID = "321"
PROJECT_ID = 123
BASE_PROJECTS_URL = f"https://{GENERAL_HOST}/api/accounts/{ACCOUNT_ID}/projects"


@pytest.fixture
def client() -> ProjectsApi:
    return ProjectsApi(account_id=ACCOUNT_ID, client=HttpClient(GENERAL_HOST))


@pytest.fixture
def sample_project_dict() -> dict[str, Any]:
    return {
        "id": PROJECT_ID,
        "name": "Test Project",
        "inboxes": [],
        "share_links": {
            "admin": "https://mailtrap.io/projects/321/admin",
            "viewer": "https://mailtrap.io/projects/321/viewer",
        },
        "permissions": {
            "can_read": True,
            "can_update": True,
            "can_destroy": True,
            "can_leave": True,
        },
    }


class TestProjectsApi:

    @pytest.mark.parametrize(
        "status_code,response_json,expected_error_message",
        [
            (
                conftest.UNAUTHORIZED_STATUS_CODE,
                conftest.UNAUTHORIZED_RESPONSE,
                conftest.UNAUTHORIZED_ERROR_MESSAGE,
            ),
            (
                conftest.FORBIDDEN_STATUS_CODE,
                conftest.FORBIDDEN_RESPONSE,
                conftest.FORBIDDEN_ERROR_MESSAGE,
            ),
        ],
    )
    @responses.activate
    def test_get_list_should_raise_api_errors(
        self,
        client: ProjectsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.get(
            BASE_PROJECTS_URL,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.get_list()

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_list_should_return_project_list(
        self, client: ProjectsApi, sample_project_dict: dict
    ) -> None:
        responses.get(
            BASE_PROJECTS_URL,
            json=[sample_project_dict],
            status=200,
        )

        projects = client.get_list()

        assert isinstance(projects, list)
        assert all(isinstance(p, Project) for p in projects)
        assert projects[0].id == PROJECT_ID

    @pytest.mark.parametrize(
        "status_code,response_json,expected_error_message",
        [
            (
                conftest.UNAUTHORIZED_STATUS_CODE,
                conftest.UNAUTHORIZED_RESPONSE,
                conftest.UNAUTHORIZED_ERROR_MESSAGE,
            ),
            (
                conftest.FORBIDDEN_STATUS_CODE,
                conftest.FORBIDDEN_RESPONSE,
                conftest.FORBIDDEN_ERROR_MESSAGE,
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
        client: ProjectsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        url = f"{BASE_PROJECTS_URL}/{PROJECT_ID}"
        responses.get(
            url,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.get_by_id(PROJECT_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_by_id_should_return_single_project(
        self, client: ProjectsApi, sample_project_dict: dict
    ) -> None:
        url = f"{BASE_PROJECTS_URL}/{PROJECT_ID}"
        responses.get(
            url,
            json=sample_project_dict,
            status=200,
        )

        project = client.get_by_id(PROJECT_ID)

        assert isinstance(project, Project)
        assert project.id == PROJECT_ID

    @pytest.mark.parametrize(
        "status_code,response_json,expected_error_message",
        [
            (
                conftest.UNAUTHORIZED_STATUS_CODE,
                conftest.UNAUTHORIZED_RESPONSE,
                conftest.UNAUTHORIZED_ERROR_MESSAGE,
            ),
            (
                conftest.FORBIDDEN_STATUS_CODE,
                conftest.FORBIDDEN_RESPONSE,
                conftest.FORBIDDEN_ERROR_MESSAGE,
            ),
        ],
    )
    @responses.activate
    def test_create_should_raise_api_errors(
        self,
        client: ProjectsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.post(
            BASE_PROJECTS_URL,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.create(project_params=ProjectParams(name="New Project"))

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_create_should_return_new_project(
        self, client: ProjectsApi, sample_project_dict: dict
    ) -> None:
        responses.post(
            BASE_PROJECTS_URL,
            json=sample_project_dict,
            status=201,
        )

        project = client.create(project_params=ProjectParams(name="New Project"))

        assert isinstance(project, Project)
        assert project.name == "Test Project"

    @pytest.mark.parametrize(
        "status_code,response_json,expected_error_message",
        [
            (
                conftest.UNAUTHORIZED_STATUS_CODE,
                conftest.UNAUTHORIZED_RESPONSE,
                conftest.UNAUTHORIZED_ERROR_MESSAGE,
            ),
            (
                conftest.FORBIDDEN_STATUS_CODE,
                conftest.FORBIDDEN_RESPONSE,
                conftest.FORBIDDEN_ERROR_MESSAGE,
            ),
            (
                conftest.NOT_FOUND_STATUS_CODE,
                conftest.NOT_FOUND_RESPONSE,
                conftest.NOT_FOUND_ERROR_MESSAGE,
            ),
        ],
    )
    @responses.activate
    def test_update_should_raise_api_errors(
        self,
        client: ProjectsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        url = f"{BASE_PROJECTS_URL}/{PROJECT_ID}"
        responses.patch(
            url,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            _ = client.update(
                PROJECT_ID, project_params=ProjectParams(name="Update Project Namet")
            )

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_update_should_return_updated_project(
        self, client: ProjectsApi, sample_project_dict: dict
    ) -> None:
        url = f"{BASE_PROJECTS_URL}/{PROJECT_ID}"
        updated_name = "Updated Project"
        updated_project_dict = sample_project_dict.copy()
        updated_project_dict["name"] = updated_name

        responses.patch(
            url,
            json=updated_project_dict,
            status=200,
        )

        project = client.update(
            PROJECT_ID, project_params=ProjectParams(name=updated_name)
        )

        assert isinstance(project, Project)
        assert project.name == updated_name

    @pytest.mark.parametrize(
        "status_code,response_json,expected_error_message",
        [
            (
                conftest.UNAUTHORIZED_STATUS_CODE,
                conftest.UNAUTHORIZED_RESPONSE,
                conftest.UNAUTHORIZED_ERROR_MESSAGE,
            ),
            (
                conftest.FORBIDDEN_STATUS_CODE,
                conftest.FORBIDDEN_RESPONSE,
                conftest.FORBIDDEN_ERROR_MESSAGE,
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
        client: ProjectsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        url = f"{BASE_PROJECTS_URL}/{PROJECT_ID}"
        responses.delete(
            url,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.delete(PROJECT_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_delete_should_return_deleted_object(self, client: ProjectsApi) -> None:
        url = f"{BASE_PROJECTS_URL}/{PROJECT_ID}"
        responses.delete(
            url,
            json={"id": PROJECT_ID},
            status=200,
        )

        result = client.delete(PROJECT_ID)

        assert isinstance(result, DeletedObject)
        assert result.id == PROJECT_ID
