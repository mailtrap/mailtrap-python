import os
from typing import Optional

import mailtrap as mt
from mailtrap.models.sandboxes import Sandbox

API_KEY = os.environ["MAILTRAP_API_KEY"]
ACCOUNT_ID = os.environ["MAILTRAP_ACCOUNT_ID"]

client = mt.MailtrapClient(token=API_KEY, account_id=ACCOUNT_ID)
sandboxes_api = client.sandbox_api.sandboxes


def list_sandboxes() -> list[Sandbox]:
    return sandboxes_api.get_list()


def create_sandbox(project_id: int, sandbox_name: str) -> Sandbox:
    return sandboxes_api.create(
        project_id=project_id, sandbox_params=mt.CreateSandboxParams(name=sandbox_name)
    )


def get_sandbox_by_id(sandbox_id: int) -> Sandbox:
    return sandboxes_api.get_by_id(sandbox_id)


def update_sandbox(
    sandbox_id: int,
    new_name: Optional[str] = None,
    new_email_username: Optional[str] = None,
) -> Sandbox:
    return sandboxes_api.update(
        sandbox_id,
        mt.UpdateSandboxParams(name=new_name, email_username=new_email_username),
    )


def clean_sandbox(sandbox_id: int) -> Sandbox:
    return sandboxes_api.clean(sandbox_id)


def mark_sandbox_as_read(sandbox_id: int) -> Sandbox:
    return sandboxes_api.mark_as_read(sandbox_id)


def reset_sandbox_credentials(sandbox_id: int) -> Sandbox:
    return sandboxes_api.reset_credentials(sandbox_id)


def enable_sandbox_email_address(sandbox_id: int) -> Sandbox:
    return sandboxes_api.enable_email_address(sandbox_id)


def reset_sandbox_email_username(sandbox_id: int) -> Sandbox:
    return sandboxes_api.reset_email_username(sandbox_id)


def delete_sandbox(sandbox_id: int):
    return sandboxes_api.delete(sandbox_id)


if __name__ == "__main__":
    sandboxes = list_sandboxes()
    print(sandboxes)

    project_id = client.sandbox_api.projects.get_list()[0].id
    created = create_sandbox(
        project_id=project_id, sandbox_name="example-created-sandbox"
    )
    print(created)

    sandbox_id = created.id
    sandbox = get_sandbox_by_id(sandbox_id=sandbox_id)
    print(sandbox)

    updated = update_sandbox(sandbox_id=sandbox_id, new_name=f"{sandbox.name}-updated")
    print(updated)

    cleaned = clean_sandbox(sandbox_id=sandbox_id)
    print(cleaned)

    marked = mark_sandbox_as_read(sandbox_id=sandbox_id)
    print(marked)

    reset_creds = reset_sandbox_credentials(sandbox_id=sandbox_id)
    print(reset_creds)

    enabled = enable_sandbox_email_address(sandbox_id=sandbox_id)
    print(enabled)

    reset_username = reset_sandbox_email_username(sandbox_id=sandbox_id)
    print(reset_username)

    deleted = delete_sandbox(sandbox_id=sandbox_id)
    print(deleted)
