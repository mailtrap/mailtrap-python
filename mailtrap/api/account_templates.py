from mailtrap.api.resources.account_templates import AccountTemplatesApi
from mailtrap.http import HttpClient


class TemplatesBaseApi:
    def __init__(self, client: HttpClient, account_id: str) -> None:
        self._account_id = account_id
        self._client = client

    @property
    def templates(self) -> AccountTemplatesApi:
        return AccountTemplatesApi(account_id=self._account_id, client=self._client)
