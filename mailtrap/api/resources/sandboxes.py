from typing import Optional

from mailtrap._deprecation import renamed_kwargs
from mailtrap.http import HttpClient
from mailtrap.models.sandboxes import CreateSandboxParams
from mailtrap.models.sandboxes import Sandbox
from mailtrap.models.sandboxes import UpdateSandboxParams


class SandboxesApi:
    def __init__(self, client: HttpClient, account_id: str) -> None:
        self._account_id = account_id
        self._client = client

    def get_list(self) -> list[Sandbox]:
        """Get a list of sandboxes."""
        response = self._client.get(self._api_path())
        return [Sandbox(**sandbox) for sandbox in response]

    @renamed_kwargs(inbox_id="sandbox_id")
    def get_by_id(self, sandbox_id: int) -> Sandbox:
        """Get sandbox attributes by sandbox id."""
        response = self._client.get(self._api_path(sandbox_id))
        return Sandbox(**response)

    @renamed_kwargs(inbox_params="sandbox_params")
    def create(self, project_id: int, sandbox_params: CreateSandboxParams) -> Sandbox:
        """Create a sandbox in a project."""
        response = self._client.post(
            f"/api/accounts/{self._account_id}/projects/{project_id}/inboxes",
            json={"inbox": sandbox_params.api_data},
        )
        return Sandbox(**response)

    @renamed_kwargs(inbox_id="sandbox_id", inbox_params="sandbox_params")
    def update(self, sandbox_id: int, sandbox_params: UpdateSandboxParams) -> Sandbox:
        """Update sandbox name, sandbox email username."""
        response = self._client.patch(
            self._api_path(sandbox_id),
            json={"inbox": sandbox_params.api_data},
        )
        return Sandbox(**response)

    @renamed_kwargs(inbox_id="sandbox_id")
    def delete(self, sandbox_id: int) -> Sandbox:
        """Delete a sandbox with all its emails."""
        response = self._client.delete(self._api_path(sandbox_id))
        return Sandbox(**response)

    @renamed_kwargs(inbox_id="sandbox_id")
    def clean(self, sandbox_id: int) -> Sandbox:
        """Delete all messages (emails) from sandbox."""
        response = self._client.patch(f"{self._api_path(sandbox_id)}/clean")
        return Sandbox(**response)

    @renamed_kwargs(inbox_id="sandbox_id")
    def mark_as_read(self, sandbox_id: int) -> Sandbox:
        """Mark all messages in the sandbox as read."""
        response = self._client.patch(f"{self._api_path(sandbox_id)}/all_read")
        return Sandbox(**response)

    @renamed_kwargs(inbox_id="sandbox_id")
    def reset_credentials(self, sandbox_id: int) -> Sandbox:
        """Reset SMTP credentials of the sandbox."""
        response = self._client.patch(f"{self._api_path(sandbox_id)}/reset_credentials")
        return Sandbox(**response)

    @renamed_kwargs(inbox_id="sandbox_id")
    def enable_email_address(self, sandbox_id: int) -> Sandbox:
        """Turn the email address of the sandbox on/off."""
        response = self._client.patch(
            f"{self._api_path(sandbox_id)}/toggle_email_username"
        )
        return Sandbox(**response)

    @renamed_kwargs(inbox_id="sandbox_id")
    def reset_email_username(self, sandbox_id: int) -> Sandbox:
        """Reset username of email address per sandbox."""
        response = self._client.patch(
            f"{self._api_path(sandbox_id)}/reset_email_username"
        )
        return Sandbox(**response)

    def _api_path(self, sandbox_id: Optional[int] = None) -> str:
        path = f"/api/accounts/{self._account_id}/inboxes"
        if sandbox_id is not None:
            return f"{path}/{sandbox_id}"
        return path
