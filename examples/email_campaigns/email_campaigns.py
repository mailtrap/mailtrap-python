from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Optional

import mailtrap as mt
from mailtrap.models.common import DeletedObject
from mailtrap.models.email_campaigns import EmailCampaign
from mailtrap.models.email_campaigns import EmailCampaignListParams
from mailtrap.models.email_campaigns import EmailCampaignListResponse
from mailtrap.models.email_campaigns import EmailCampaignStats
from mailtrap.models.email_campaigns import EmailCampaignStatsParams

API_TOKEN = "YOUR_API_TOKEN"
DOMAIN_ID = 4321

client = mt.MailtrapClient(token=API_TOKEN)
email_campaigns_api = client.email_campaigns_api.email_campaigns


def list_email_campaigns() -> EmailCampaignListResponse:
    # `search` filters by name; `token` is the page number (page-token
    # pagination); `per_page` caps at 100 (default 50).
    return email_campaigns_api.get_list(
        EmailCampaignListParams(per_page=50, search="Spring", token=1)
    )


def get_email_campaign(email_campaign_id: int) -> EmailCampaign:
    return email_campaigns_api.get_by_id(email_campaign_id=email_campaign_id)


def find_subscription_topic_id(domain_id: int) -> Optional[int]:
    # A topic covers the campaign's domain when its `domain_id` is that domain
    # or None (every domain). The list answers 403 when the account has no
    # subscription topics.
    try:
        topics = client.subscription_topics_api.subscription_topics.get_list()
    except mt.APIError as error:
        if error.status == 403:
            return None
        raise
    return next(
        (topic.id for topic in topics.data if topic.domain_id in (None, domain_id)),
        None,
    )


def create_email_campaign() -> EmailCampaign:
    # A campaign is created in the `draft` state and must reference a verified
    # sending domain via `domain_id` (as returned by the Sending Domains
    # endpoints). `subscription_topic_id` is left out of the request when None.
    return email_campaigns_api.create(
        mt.CreateEmailCampaignParams(
            name="Spring Sale",
            domain_id=DOMAIN_ID,
            from_display_name="Acme Marketing",
            from_local_part="news",
            reply_to=mt.EmailCampaignReplyTo(
                display_name="Acme Support",
                local_part="support",
                domain="acme.com",
            ),
            template_attributes=mt.CreateEmailCampaignTemplateAttributes(
                subject="Spring is here — 30% off"
            ),
            subscription_topic_id=find_subscription_topic_id(DOMAIN_ID),
        )
    )


def update_email_campaign(email_campaign_id: int) -> EmailCampaign:
    # Only supplied fields are changed. The campaign's template is edited in
    # place — pass only the `template_attributes` sub-fields you want changed.
    return email_campaigns_api.update(
        email_campaign_id=email_campaign_id,
        campaign_params=mt.UpdateEmailCampaignParams(
            name="Spring Sale (updated)",
            delivery_mode="gradual",
            delivery_options=mt.EmailCampaignDeliveryOptions(emails_per_hour=1000),
            contact_list_ids=[55, 56],
            contact_segment_ids=[12],
            template_attributes=mt.EmailCampaignTemplateAttributes(
                subject="Spring is here — 30% off everything",
                body_html=(
                    "<html><body>"
                    "<h1>Hi {{first_name}}!</h1>"
                    '<p><a href="__unsubscribe_url__">Unsubscribe</a></p>'
                    "</body></html>"
                ),
                merge_tags=["first_name"],
            ),
        ),
    )


def schedule_email_campaign(email_campaign_id: int) -> EmailCampaign:
    # The campaign must be a `draft`; the time must be in the future (at most
    # 1 month ahead) and comes back in `current_state_metadata.scheduled_at`.
    send_at = datetime.now(timezone.utc) + timedelta(days=1)
    return email_campaigns_api.schedule(
        email_campaign_id=email_campaign_id,
        schedule_params=mt.ScheduleEmailCampaignParams(
            datetime=send_at.isoformat(timespec="milliseconds").replace("+00:00", "Z")
        ),
    )


def cancel_email_campaign(email_campaign_id: int) -> EmailCampaign:
    # Cancels a `scheduled` campaign, returning it to `draft`.
    return email_campaigns_api.cancel(email_campaign_id=email_campaign_id)


def start_email_campaign(email_campaign_id: int) -> EmailCampaign:
    # Starts sending a `draft` campaign immediately.
    return email_campaigns_api.start(email_campaign_id=email_campaign_id)


def terminate_email_campaign(email_campaign_id: int) -> EmailCampaign:
    # Aborts a campaign that is currently sending.
    return email_campaigns_api.terminate(email_campaign_id=email_campaign_id)


def reset_email_campaign(email_campaign_id: int) -> EmailCampaign:
    # Resets a `scheduled` campaign back to `draft`.
    return email_campaigns_api.reset(email_campaign_id=email_campaign_id)


def get_email_campaign_stats(email_campaign_id: int) -> EmailCampaignStats:
    today = datetime.now(timezone.utc).date()
    return email_campaigns_api.get_stats(
        email_campaign_id=email_campaign_id,
        params=EmailCampaignStatsParams(
            start_date=(today - timedelta(days=30)).isoformat(),
            end_date=today.isoformat(),
        ),
    )


def delete_email_campaign(email_campaign_id: int) -> DeletedObject:
    # The API responds with 204 No Content.
    return email_campaigns_api.delete(email_campaign_id=email_campaign_id)


if __name__ == "__main__":
    listed = list_email_campaigns()
    print(listed.data)
    print(listed.pagination)

    created = create_email_campaign()
    print(created)

    fetched = get_email_campaign(created.id)
    print(fetched)

    updated = update_email_campaign(created.id)
    print(updated)

    scheduled = schedule_email_campaign(created.id)
    print(scheduled.current_state_metadata)

    cancelled = cancel_email_campaign(created.id)
    print(cancelled.current_state)

    started = start_email_campaign(created.id)
    print(started.current_state)

    stats = get_email_campaign_stats(created.id)
    print(stats)

    # Only a campaign in the `draft` state can be deleted, and a campaign that
    # has been started can never return to `draft` — so delete a fresh draft
    # rather than the one started above.
    throwaway = create_email_campaign()
    deleted = delete_email_campaign(throwaway.id)
    print(deleted)
