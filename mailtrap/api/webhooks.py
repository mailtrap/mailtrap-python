from mailtrap.api.resources.webhooks import WebhooksApi
from mailtrap.http import HttpClient


class WebhooksBaseApi:
    def __init__(self, client: HttpClient, account_id: str) -> None:
        self._account_id = account_id
        self._client = client

    @property
    def webhooks(self) -> WebhooksApi:
        return WebhooksApi(account_id=self._account_id, client=self._client)
