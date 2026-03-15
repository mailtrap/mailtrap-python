from mailtrap.api.resources.email_logs import EmailLogsApi
from mailtrap.http import HttpClient


class EmailLogsBaseApi:
    def __init__(self, client: HttpClient, account_id: str) -> None:
        self._account_id = account_id
        self._client = client

    @property
    def email_logs(self) -> EmailLogsApi:
        return EmailLogsApi(client=self._client, account_id=self._account_id)
