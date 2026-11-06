from typing import Optional

from mailtrap.http import HttpClient
from mailtrap.models.common import DeletedObject
from mailtrap.models.projects import Project
from mailtrap.models.projects import ProjectParams


class ProjectsApi:
    def __init__(self, client: HttpClient, account_id: str) -> None:
        self._account_id = account_id
        self._client = client

    def get_list(self) -> list[Project]:
        """List projects and their sandboxes to which the API token has access."""
        response = self._client.get(self._api_path())
        return [Project(**project) for project in response]

    def get_by_id(self, project_id: int) -> Project:
        """Get the project and its sandboxes."""
        response = self._client.get(self._api_path(project_id))
        return Project(**response)

    def create(self, project_params: ProjectParams) -> Project:
        """
        Create a new project.
        The project name is min 2 characters and max 100 characters long.
        """
        response = self._client.post(
            self._api_path(),
            json={"project": project_params.api_data},
        )
        return Project(**response)

    def update(self, project_id: int, project_params: ProjectParams) -> Project:
        """
        Update project name.
        The project name is min 2 characters and max 100 characters long.
        """
        response = self._client.patch(
            self._api_path(project_id),
            json={"project": project_params.api_data},
        )
        return Project(**response)

    def delete(self, project_id: int) -> DeletedObject:
        """Delete project and its sandboxes."""
        response = self._client.delete(self._api_path(project_id))
        return DeletedObject(**response)

    def _api_path(self, project_id: Optional[int] = None) -> str:
        path = f"/api/accounts/{self._account_id}/projects"
        if project_id:
            return f"{path}/{project_id}"
        return path
