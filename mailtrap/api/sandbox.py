from mailtrap.api.resources.attachments import AttachmentsApi
from mailtrap.api.resources.messages import MessagesApi
from mailtrap.api.resources.projects import ProjectsApi
from mailtrap.api.resources.sandboxes import SandboxesApi
from mailtrap.http import HttpClient


class SandboxApi:
    def __init__(self, client: HttpClient, account_id: str) -> None:
        self._account_id = account_id
        self._client = client

    @property
    def projects(self) -> ProjectsApi:
        return ProjectsApi(account_id=self._account_id, client=self._client)

    @property
    def sandboxes(self) -> SandboxesApi:
        return SandboxesApi(account_id=self._account_id, client=self._client)

    @property
    def messages(self) -> MessagesApi:
        return MessagesApi(account_id=self._account_id, client=self._client)

    @property
    def attachments(self) -> AttachmentsApi:
        return AttachmentsApi(account_id=self._account_id, client=self._client)
