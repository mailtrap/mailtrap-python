import mailtrap as mt
from mailtrap.models.billing import BillingCycleUsage

API_TOKEN = "YOUR_API_TOKEN"
ACCOUNT_ID = "YOUR_ACCOUNT_ID"

client = mt.MailtrapClient(token=API_TOKEN)
billing_api = client.general_api.billing


def get_current_billing_usage(account_id: int) -> BillingCycleUsage:
    return billing_api.get_current_billing_usage(account_id=account_id)


if __name__ == "__main__":
    print(get_current_billing_usage(ACCOUNT_ID))
