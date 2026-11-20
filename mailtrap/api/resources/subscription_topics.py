from typing import Optional

from mailtrap.http import HttpClient
from mailtrap.models.subscription_topics import SubscriptionTopic
from mailtrap.models.subscription_topics import SubscriptionTopicListParams
from mailtrap.models.subscription_topics import SubscriptionTopicListResponse
from mailtrap.models.subscription_topics import SubscriptionTopicResponse


class SubscriptionTopicsApi:
    """
    Subscription Topics API. On an account without subscription topics, both
    calls raise ``APIError`` with status ``403``.
    """

    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def get_list(
        self, params: Optional[SubscriptionTopicListParams] = None
    ) -> SubscriptionTopicListResponse:
        """
        List the account's subscription topics, one page at a time, leaving out
        deleted ones. Pass ``pagination.next_token`` with the same ``per_page``
        to get the next page. Omit ``params`` for the first page with API
        defaults.
        """
        query_params = params.api_query_params if params else None
        response = self._client.get(self._api_path(), params=query_params or None)
        return SubscriptionTopicListResponse(**response)

    def get_by_id(self, subscription_topic_id: int) -> SubscriptionTopic:
        """
        Get a subscription topic by ID. A deleted topic is returned too, with
        ``deleted_at`` set.
        """
        response = self._client.get(self._api_path(subscription_topic_id))
        return SubscriptionTopicResponse(**response).data

    def _api_path(self, subscription_topic_id: Optional[int] = None) -> str:
        path = "/api/subscription_topics"
        if subscription_topic_id is not None:
            return f"{path}/{subscription_topic_id}"
        return path
