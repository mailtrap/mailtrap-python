import os

import mailtrap as mt
from mailtrap.models.common import DeletedObject
from mailtrap.models.webhooks import Webhook
from mailtrap.models.webhooks import WebhookWithSecret

API_KEY = os.environ["MAILTRAP_API_KEY"]
ACCOUNT_ID = os.environ["MAILTRAP_ACCOUNT_ID"]

client = mt.MailtrapClient(token=API_KEY, account_id=ACCOUNT_ID)
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


def create_bulk_webhook() -> WebhookWithSecret:
    # `subscription_preferences_update` is sent when a contact changes their
    # subscription topic preferences. It is available only for the bulk stream
    # and on `campaigns` webhooks.
    return webhooks_api.create(
        mt.CreateWebhookParams(
            url="https://example.com/mailtrap/webhooks",
            webhook_type="email_sending",
            sending_stream="bulk",
            event_types=["delivery", "unsubscribe", "subscription_preferences_update"],
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
