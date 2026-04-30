from typing import Optional

from mailtrap.http import HttpClient
from mailtrap.models.common import DeletedObject
from mailtrap.models.webhooks import CreateWebhookParams
from mailtrap.models.webhooks import UpdateWebhookParams
from mailtrap.models.webhooks import Webhook
from mailtrap.models.webhooks import WebhookCreateResponse
from mailtrap.models.webhooks import WebhookListResponse
from mailtrap.models.webhooks import WebhookResponse
from mailtrap.models.webhooks import WebhookWithSecret


class WebhooksApi:
    def __init__(self, client: HttpClient, account_id: str) -> None:
        self._account_id = account_id
        self._client = client

    def get_list(self) -> list[Webhook]:
        """
        List all webhooks for the account.
        """
        response = self._client.get(self._api_path())
        return WebhookListResponse(**response).data

    def get_by_id(self, webhook_id: int) -> Webhook:
        """
        Get a single webhook by id.
        """
        response = self._client.get(self._api_path(webhook_id))
        return WebhookResponse(**response).data

    def create(self, webhook_params: CreateWebhookParams) -> WebhookWithSecret:
        """
        Create a new webhook. The response includes a `signing_secret` used
        to verify webhook signatures — store it securely; it is only
        returned once on creation.
        """
        response = self._client.post(
            self._api_path(), json={"webhook": webhook_params.api_data}
        )
        return WebhookCreateResponse(**response).data

    def update(
        self, webhook_id: int, webhook_params: UpdateWebhookParams
    ) -> Webhook:
        """
        Update an existing webhook. Only the fields supplied in
        `webhook_params` are sent to the API.
        """
        response = self._client.patch(
            self._api_path(webhook_id),
            json={"webhook": webhook_params.api_data},
        )
        return WebhookResponse(**response).data

    def delete(self, webhook_id: int) -> DeletedObject:
        """
        Permanently delete a webhook.
        """
        self._client.delete(self._api_path(webhook_id))
        return DeletedObject(id=webhook_id)

    def _api_path(self, webhook_id: Optional[int] = None) -> str:
        path = f"/api/accounts/{self._account_id}/webhooks"
        if webhook_id is not None:
            return f"{path}/{webhook_id}"
        return path
