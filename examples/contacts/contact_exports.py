import mailtrap as mt
from mailtrap.models.contacts import ContactExportDetail

API_TOKEN = "YOUR_API_TOKEN"
ACCOUNT_ID = "YOUR_ACCOUNT_ID"

client = mt.MailtrapClient(token=API_TOKEN, account_id=ACCOUNT_ID)
contact_exports_api = client.contacts_api.contact_exports


def create_export_contacts(
    contact_exports_params: mt.CreateContactExportParams,
) -> ContactExportDetail:
    return contact_exports_api.create(contact_exports_params=contact_exports_params)


def get_contact_export(export_id: int) -> ContactExportDetail:
    return contact_exports_api.get_by_id(export_id)


if __name__ == "__main__":
    contact_export = create_export_contacts(
        contact_exports_params=mt.CreateContactExportParams(
            filters=[mt.ContactExportFilter(name="list_id", operator="equal", value=[10])]
        )
    )
    print(contact_export)

    contact_export = get_contact_export(contact_export.id)
    print(contact_export)
