import mailtrap as mt
from mailtrap.models.projects import Project

API_TOKEN = "YOUR_API_TOKEN"
ACCOUNT_ID = "YOUR_ACCOUNT_ID"

client = mt.MailtrapClient(token=API_TOKEN, account_id=ACCOUNT_ID)
projects_api = client.testing_api.projects


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
    created = create_project(name="example-created-project")
    print(created)

    projects = list_projects()
    print(projects)

    project_id = projects[0].id

    project = get_project(project_id=project_id)
    print(project)

    updated = update_project(project_id=created.id, new_name=f"{project.name}-updated")
    print(updated)

    deleted = delete_project(project_id=created.id)
    print(deleted)
