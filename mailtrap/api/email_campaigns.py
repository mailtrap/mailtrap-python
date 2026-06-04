from mailtrap.api.resources.email_campaigns import EmailCampaignsApi
from mailtrap.http import HttpClient


class EmailCampaignsBaseApi:
    def __init__(self, client: HttpClient, account_id: str) -> None:
        self._account_id = account_id
        self._client = client

    @property
    def email_campaigns(self) -> EmailCampaignsApi:
        return EmailCampaignsApi(account_id=self._account_id, client=self._client)
