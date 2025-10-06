from mailtrap.api.resources.contact_exports import ContactExportsApi
from mailtrap.api.resources.contact_fields import ContactFieldsApi
from mailtrap.api.resources.contact_imports import ContactImportsApi
from mailtrap.api.resources.contact_lists import ContactListsApi
from mailtrap.api.resources.contacts import ContactsApi
from mailtrap.http import HttpClient


class ContactsBaseApi:
    def __init__(self, client: HttpClient, account_id: str) -> None:
        self._account_id = account_id
        self._client = client

    @property
    def contact_exports(self) -> ContactExportsApi:
        return ContactExportsApi(account_id=self._account_id, client=self._client)

    @property
    def contact_fields(self) -> ContactFieldsApi:
        return ContactFieldsApi(account_id=self._account_id, client=self._client)

    @property
    def contact_lists(self) -> ContactListsApi:
        return ContactListsApi(account_id=self._account_id, client=self._client)

    @property
    def contact_imports(self) -> ContactImportsApi:
        return ContactImportsApi(account_id=self._account_id, client=self._client)

    @property
    def contacts(self) -> ContactsApi:
        return ContactsApi(account_id=self._account_id, client=self._client)
