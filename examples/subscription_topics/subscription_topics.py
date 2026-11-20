import os
from typing import Optional

import mailtrap as mt
from mailtrap.models.subscription_topics import SubscriptionTopic
from mailtrap.models.subscription_topics import SubscriptionTopicListResponse

API_KEY = os.environ["MAILTRAP_API_KEY"]

client = mt.MailtrapClient(token=API_KEY)
subscription_topics_api = client.subscription_topics_api.subscription_topics


def list_subscription_topics(
    token: Optional[int] = None,
) -> SubscriptionTopicListResponse:
    # `token` is the page number (page-token pagination); `per_page` caps at
    # 100 (default 50). Deleted topics are left out.
    return subscription_topics_api.get_list(
        mt.SubscriptionTopicListParams(per_page=50, token=token)
    )


def get_subscription_topic(subscription_topic_id: int) -> SubscriptionTopic:
    # A deleted topic is returned too, with `deleted_at` set.
    return subscription_topics_api.get_by_id(subscription_topic_id)


if __name__ == "__main__":
    try:
        page = list_subscription_topics()
    except mt.APIError as error:
        if error.status != 403:
            raise
        raise SystemExit("Subscription topics aren't available for this account.")

    while True:
        for topic in page.data:
            # `domain_id` is None when the topic covers every sending domain.
            print(f"{topic.id}: {topic.name} (domain: {topic.domain_id or 'all'})")
        if page.pagination is None or page.pagination.next_token is None:
            break
        page = list_subscription_topics(token=page.pagination.next_token)

    if page.data:
        print(get_subscription_topic(page.data[0].id))
