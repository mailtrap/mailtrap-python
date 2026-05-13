import mailtrap as mt
from mailtrap.models.common import DeletedObject
from mailtrap.models.webhooks import Webhook
from mailtrap.models.webhooks import WebhookWithSecret

API_TOKEN = "YOUR_API_TOKEN"
ACCOUNT_ID = "YOUR_ACCOUNT_ID"

client = mt.MailtrapClient(token=API_TOKEN, account_id=ACCOUNT_ID)
webhooks_api = client.webhooks_api.webhooks


def list_webhooks() -> list[Webhook]:
    return webhooks_api.get_list()


def get_webhook(webhook_id: int) -> Webhook:
    return webhooks_api.get_by_id(webhook_id=webhook_id)


def create_webhook() -> WebhookWithSecret:
    # The signing_secret is only returned once on creation — store it
    # securely and use it to verify webhook signatures (HMAC SHA-256).
    return webhooks_api.create(
        mt.CreateWebhookParams(
            url="https://example.com/mailtrap/webhooks",
            webhook_type="email_sending",
            sending_stream="transactional",
            event_types=["delivery", "bounce"],
        )
    )


def update_webhook(webhook_id: int) -> Webhook:
    return webhooks_api.update(
        webhook_id=webhook_id,
        webhook_params=mt.UpdateWebhookParams(active=False),
    )


def delete_webhook(webhook_id: int) -> DeletedObject:
    return webhooks_api.delete(webhook_id=webhook_id)


if __name__ == "__main__":
    webhooks = list_webhooks()
    print(webhooks)

    created = create_webhook()
    print(created)

    fetched = get_webhook(created.id)
    print(fetched)

    updated = update_webhook(created.id)
    print(updated)

    deleted = delete_webhook(created.id)
    print(deleted)
