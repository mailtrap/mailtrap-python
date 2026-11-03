import os

import mailtrap as mt
from mailtrap.models.projects import Project

API_KEY = os.environ["MAILTRAP_API_KEY"]
ACCOUNT_ID = os.environ["MAILTRAP_ACCOUNT_ID"]

client = mt.MailtrapClient(token=API_KEY, account_id=ACCOUNT_ID)
projects_api = client.sandbox_api.projects


def list_projects() -> list[Project]:
    return projects_api.get_list()


def get_project(project_id: int) -> Project:
    return projects_api.get_by_id(project_id)


def create_project(name: str) -> Project:
    return projects_api.create(project_params=mt.ProjectParams(name=name))


def update_project(project_id: int, new_name: str) -> Project:
    return projects_api.update(project_id, mt.ProjectParams(name=new_name))


def delete_project(project_id: int):
    return projects_api.delete(project_id)


if __name__ == "__main__":
    projects = list_projects()
    print(projects)

    created = create_project(name="example-created-project")
    print(created)

    project = get_project(project_id=created.id)
    print(project)

    updated = update_project(project_id=created.id, new_name=f"{project.name}-updated")
    print(updated)

    deleted = delete_project(project_id=created.id)
    print(deleted)
