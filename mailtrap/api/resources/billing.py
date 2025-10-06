from mailtrap.http import HttpClient
from mailtrap.models.billing import BillingCycleUsage


class BillingApi:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def get_current_billing_usage(self, account_id: int) -> BillingCycleUsage:
        """Get current billing cycle usage for Email Testing and Email Sending."""
        response = self._client.get(f"/api/accounts/{account_id}/billing/usage")
        return BillingCycleUsage(**response)
