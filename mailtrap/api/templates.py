from mailtrap.api.resources.templates import TemplatesApi
from mailtrap.http import HttpClient


class EmailTemplatesApi:
    def __init__(self, client: HttpClient, account_id: str) -> None:
        self._account_id = account_id
        self._client = client

    @property
    def templates(self) -> TemplatesApi:
        return TemplatesApi(account_id=self._account_id, client=self._client)
