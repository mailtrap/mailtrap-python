from mailtrap.api.resources.subscription_topics import SubscriptionTopicsApi
from mailtrap.http import HttpClient


class SubscriptionTopicsBaseApi:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    @property
    def subscription_topics(self) -> SubscriptionTopicsApi:
        return SubscriptionTopicsApi(client=self._client)
