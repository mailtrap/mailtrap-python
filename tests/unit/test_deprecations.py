"""
The Testing, Inbox and SendingDomain names are deprecated aliases of the Sandbox
and Domain names. Each test checks that an old name still works and warns.
"""

import pytest
import responses

import mailtrap as mt
from mailtrap._deprecation import renamed_kwargs
from mailtrap.api import testing  # module import: pytest would collect TestingApi
from mailtrap.api.domains import DomainsBaseApi
from mailtrap.api.resources.company_info import CompanyInfoApi
from mailtrap.api.resources.domains import DomainsApi
from mailtrap.api.resources.inboxes import InboxesApi
from mailtrap.api.resources.messages import MessagesApi
from mailtrap.api.resources.sandboxes import SandboxesApi
from mailtrap.api.resources.sending_domains import SendingDomainsApi
from mailtrap.api.sandbox import SandboxApi
from mailtrap.api.sending import SendingApi
from mailtrap.api.sending_domains import SendingDomainsBaseApi
from mailtrap.config import GENERAL_HOST
from mailtrap.config import SENDING_HOST
from mailtrap.http import HttpClient
from mailtrap.models import domains as domain_models
from mailtrap.models import inboxes as inbox_models
from mailtrap.models import sandboxes as sandbox_models
from mailtrap.models import sending_domains as sending_domain_models

ACCOUNT_ID = "321"
SANDBOX_ID = 3538
DOMAIN_ID = 432
MESSAGES_URL = (
    f"https://{GENERAL_HOST}/api/accounts/{ACCOUNT_ID}/inboxes/{SANDBOX_ID}/messages"
)
COMPANY_INFO_URL = f"https://{GENERAL_HOST}/api/domains/{DOMAIN_ID}/company_info"


@pytest.fixture
def client_with_account() -> mt.MailtrapClient:
    return mt.MailtrapClient(token="fake_token", account_id=ACCOUNT_ID)


def test_testing_api_is_deprecated_alias_of_sandbox_api(
    client_with_account: mt.MailtrapClient,
) -> None:
    with pytest.warns(
        DeprecationWarning, match=r"testing_api is deprecated.*sandbox_api"
    ) as record:
        api = client_with_account.testing_api

    assert isinstance(api, SandboxApi)
    assert record[0].filename == __file__  # points at the caller's line


def test_testing_api_inboxes_is_deprecated_alias_of_sandboxes() -> None:
    testing_api = testing.TestingApi(
        client=HttpClient(GENERAL_HOST), account_id=ACCOUNT_ID
    )

    with pytest.warns(DeprecationWarning, match=r"inboxes is deprecated.*sandboxes"):
        api = testing_api.inboxes

    assert isinstance(api, SandboxesApi)


def test_inboxes_api_is_deprecated_subclass_of_sandboxes_api() -> None:
    with pytest.warns(
        DeprecationWarning, match=r"InboxesApi is deprecated.*SandboxesApi"
    ):
        api = InboxesApi(client=HttpClient(GENERAL_HOST), account_id=ACCOUNT_ID)

    assert isinstance(api, SandboxesApi)


def test_sending_domains_api_is_deprecated_alias_of_domains_api(
    client_with_account: mt.MailtrapClient,
) -> None:
    with pytest.warns(
        DeprecationWarning, match=r"sending_domains_api is deprecated.*domains_api"
    ):
        api = client_with_account.sending_domains_api

    assert isinstance(api, DomainsBaseApi)


def test_sending_domains_is_deprecated_alias_of_domains() -> None:
    sending_domains_api = SendingDomainsBaseApi(
        client=HttpClient(GENERAL_HOST), account_id=ACCOUNT_ID
    )

    with pytest.warns(
        DeprecationWarning, match=r"sending_domains is deprecated.*domains"
    ):
        api = sending_domains_api.sending_domains

    assert isinstance(api, DomainsApi)


def test_sending_domains_api_class_is_deprecated_subclass_of_domains_api() -> None:
    with pytest.warns(
        DeprecationWarning, match=r"SendingDomainsApi is deprecated.*DomainsApi"
    ):
        api = SendingDomainsApi(client=HttpClient(GENERAL_HOST), account_id=ACCOUNT_ID)

    assert isinstance(api, DomainsApi)


def test_client_inbox_id_argument_is_deprecated_alias_of_sandbox_id() -> None:
    with pytest.warns(DeprecationWarning, match=r"inbox_id=.*is deprecated.*sandbox_id"):
        client = mt.MailtrapClient(token="fake_token", sandbox=True, inbox_id="12345")

    assert client.sandbox_id == "12345"


def test_client_inbox_id_argument_still_validates_sandbox_mode() -> None:
    with pytest.warns(DeprecationWarning, match="inbox_id"):
        with pytest.raises(mt.ClientConfigurationError, match="sandbox_id"):
            mt.MailtrapClient(token="fake_token", inbox_id="12345")


def test_client_accepts_same_inbox_id_and_sandbox_id() -> None:
    with pytest.warns(DeprecationWarning, match="inbox_id"):
        client = mt.MailtrapClient(
            token="fake_token", sandbox=True, inbox_id="12345", sandbox_id="12345"
        )

    assert client.sandbox_id == "12345"


def test_client_rejects_different_inbox_id_and_sandbox_id() -> None:
    with pytest.warns(DeprecationWarning, match="inbox_id"):
        with pytest.raises(mt.ClientConfigurationError, match="pass only `sandbox_id`"):
            mt.MailtrapClient(
                token="fake_token", sandbox=True, inbox_id="1", sandbox_id="2"
            )


def test_client_inbox_id_property_is_deprecated_alias_of_sandbox_id() -> None:
    client = mt.MailtrapClient(token="fake_token", sandbox=True, sandbox_id="12345")

    with pytest.warns(DeprecationWarning, match=r"inbox_id is deprecated.*sandbox_id"):
        assert client.inbox_id == "12345"

    with pytest.warns(DeprecationWarning, match=r"inbox_id is deprecated.*sandbox_id"):
        client.inbox_id = "67890"

    assert client.sandbox_id == "67890"


@responses.activate
def test_sending_api_inbox_id_argument_is_deprecated_alias_of_sandbox_id() -> None:
    responses.post(
        f"https://{SENDING_HOST}/api/send/12345",
        json={"success": True, "message_ids": ["1"]},
    )
    mail = mt.Mail(
        sender=mt.Address(email="joe@mail.com"),
        to=[mt.Address(email="joe@mail.com")],
        subject="Email subject",
        text="email text",
    )

    with pytest.warns(DeprecationWarning, match=r"inbox_id=.*is deprecated.*sandbox_id"):
        api = SendingApi(client=HttpClient(SENDING_HOST), inbox_id="12345")

    assert api.send(mail).success is True


@responses.activate
def test_messages_inbox_id_keyword_is_deprecated_alias_of_sandbox_id() -> None:
    responses.get(MESSAGES_URL, json=[])
    api = MessagesApi(client=HttpClient(GENERAL_HOST), account_id=ACCOUNT_ID)

    with pytest.warns(
        DeprecationWarning, match=r"get_list\(inbox_id=.*is deprecated.*sandbox_id"
    ):
        messages = api.get_list(inbox_id=SANDBOX_ID)  # type: ignore[call-arg]

    assert messages == []
    assert len(responses.calls) == 1


def test_renamed_keyword_rejects_old_and_new_together() -> None:
    api = MessagesApi(client=HttpClient(GENERAL_HOST), account_id=ACCOUNT_ID)

    with pytest.raises(TypeError, match="got both 'inbox_id' and 'sandbox_id'"):
        api.get_list(inbox_id=1, sandbox_id=1)  # type: ignore[call-arg]


def test_renamed_kwargs_maps_each_old_keyword() -> None:
    @renamed_kwargs(inbox_id="sandbox_id", inbox_params="sandbox_params")
    def update(sandbox_id: int, sandbox_params: str) -> tuple[int, str]:
        return sandbox_id, sandbox_params

    with pytest.warns(DeprecationWarning) as record:
        result = update(inbox_id=1, inbox_params="params")  # type: ignore[call-arg]

    assert result == (1, "params")
    assert len(record) == 2


@responses.activate
def test_company_info_sending_domain_id_keyword_is_deprecated() -> None:
    responses.get(COMPANY_INFO_URL, json={"data": {}})
    api = CompanyInfoApi(client=HttpClient(GENERAL_HOST))

    with pytest.warns(
        DeprecationWarning, match=r"get\(sending_domain_id=.*is deprecated.*domain_id"
    ):
        api.get(sending_domain_id=DOMAIN_ID)  # type: ignore[call-arg]

    assert len(responses.calls) == 1


def test_inbox_models_are_aliases_of_sandbox_models() -> None:
    assert inbox_models.Inbox is sandbox_models.Sandbox
    assert mt.CreateInboxParams is mt.CreateSandboxParams
    assert mt.UpdateInboxParams is mt.UpdateSandboxParams


def test_sending_domain_models_are_aliases_of_domain_models() -> None:
    assert sending_domain_models.SendingDomain is domain_models.Domain
    assert (
        sending_domain_models.SendingDomainPermissions is domain_models.DomainPermissions
    )
    assert mt.CreateSendingDomainParams is mt.CreateDomainParams
    assert mt.UpdateSendingDomainParams is mt.UpdateDomainParams
