import mailtrap as mt
from mailtrap.models.email_campaigns import EmailCampaign
from mailtrap.models.email_campaigns import EmailCampaignListResponse
from mailtrap.models.email_campaigns import EmailCampaignStats

API_TOKEN = "YOUR_API_TOKEN"
ACCOUNT_ID = "YOUR_ACCOUNT_ID"

client = mt.MailtrapClient(token=API_TOKEN, account_id=ACCOUNT_ID)
email_campaigns_api = client.email_campaigns_api.email_campaigns


def list_email_campaigns() -> EmailCampaignListResponse:
    # `search` filters by name (case-insensitive partial match); `token` is the
    # page number (page-token pagination); `per_page` caps at 100 (default 50).
    return email_campaigns_api.get_list(per_page=50, search="Spring", token=1)


def get_email_campaign(email_campaign_id: int) -> EmailCampaign:
    return email_campaigns_api.get_by_id(email_campaign_id=email_campaign_id)


def create_email_campaign() -> EmailCampaign:
    # A campaign is created in the `draft` state and must reference a verified
    # sending domain via `mailsend_domain_id`.
    return email_campaigns_api.create(
        mt.CreateEmailCampaignParams(
            name="Spring Sale",
            mailsend_domain_id=123,
            from_display_name="Acme Marketing",
            from_local_part="news",
            reply_to=mt.ReplyTo(
                display_name="Acme Support",
                local_part="support",
                domain="acme.com",
            ),
            template_attributes=mt.CampaignTemplate(subject="Spring is here — 30% off"),
        )
    )


def update_email_campaign(email_campaign_id: int, template_id: int) -> EmailCampaign:
    # Only supplied fields are changed. Pass the existing template `id` to
    # update its subject in place instead of creating a new template.
    return email_campaigns_api.update(
        email_campaign_id=email_campaign_id,
        campaign_params=mt.UpdateEmailCampaignParams(
            name="Spring Sale (updated)",
            delivery_mode="scheduled",
            scheduled_for="2026-06-01T09:00:00.000Z",
            delivery_options=mt.DeliveryOptions(emails_per_hour=1000),
            template_attributes=mt.CampaignTemplate(
                id=template_id, subject="New subject"
            ),
        ),
    )


def delete_email_campaign(email_campaign_id: int) -> EmailCampaign:
    # The deleted campaign object is returned (HTTP 200 + body).
    return email_campaigns_api.delete(email_campaign_id=email_campaign_id)


def get_email_campaign_stats(email_campaign_id: int) -> EmailCampaignStats:
    return email_campaigns_api.get_stats(email_campaign_id=email_campaign_id)


if __name__ == "__main__":
    listed = list_email_campaigns()
    print(listed.data)
    print(listed.pagination)

    created = create_email_campaign()
    print(created)

    fetched = get_email_campaign(created.id)
    print(fetched)

    template_id = created.template.id if created.template else 0
    updated = update_email_campaign(created.id, template_id)
    print(updated)

    stats = get_email_campaign_stats(created.id)
    print(stats)

    deleted = delete_email_campaign(created.id)
    print(deleted)
