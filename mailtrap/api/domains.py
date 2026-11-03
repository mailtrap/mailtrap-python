from mailtrap.api.resources.domains import DomainsApi
from mailtrap.http import HttpClient


class DomainsBaseApi:
    def __init__(self, client: HttpClient, account_id: str) -> None:
        self._account_id = account_id
        self._client = client

    @property
    def domains(self) -> DomainsApi:
        return DomainsApi(account_id=self._account_id, client=self._client)
