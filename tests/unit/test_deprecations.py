"""
The Testing, Inbox and SendingDomain names are deprecated aliases of the Sandbox
and Domain names. Each test checks that an old name still works and warns.
"""

from typing import Any

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
SANDBOXES_URL = f"https://{GENERAL_HOST}/api/accounts/{ACCOUNT_ID}/inboxes"
MESSAGES_URL = f"{SANDBOXES_URL}/{SANDBOX_ID}/messages"
DOMAINS_URL = f"https://{GENERAL_HOST}/api/accounts/{ACCOUNT_ID}/sending_domains"
COMPANY_INFO_URL = f"https://{GENERAL_HOST}/api/domains/{DOMAIN_ID}/company_info"


@pytest.fixture
def client_with_account() -> mt.MailtrapClient:
    return mt.MailtrapClient(token="fake_token", account_id=ACCOUNT_ID)


@pytest.mark.parametrize(
    ("old_cls", "new_cls"),
    [
        (testing.TestingApi, SandboxApi),
        (InboxesApi, SandboxesApi),
        (SendingDomainsBaseApi, DomainsBaseApi),
        (SendingDomainsApi, DomainsApi),
    ],
)
def test_old_api_class_is_deprecated_subclass_of_new_one(
    old_cls: type[Any], new_cls: type[Any]
) -> None:
    with pytest.warns(
        DeprecationWarning,
        match=rf"^{old_cls.__name__} is deprecated.*use {new_cls.__name__} instead",
    ) as record:
        api = old_cls(client=HttpClient(GENERAL_HOST), account_id=ACCOUNT_ID)

    assert isinstance(api, new_cls)
    assert record[0].filename == __file__  # points at the caller's line


def test_testing_api_is_deprecated_alias_of_sandbox_api(
    client_with_account: mt.MailtrapClient,
) -> None:
    with pytest.warns(
        DeprecationWarning, match=r"testing_api is deprecated.*sandbox_api"
    ) as record:
        api = client_with_account.testing_api

    assert isinstance(api, testing.TestingApi)
    assert len(record) == 1
    assert record[0].filename == __file__


@responses.activate
def test_testing_api_inboxes_is_deprecated_alias_of_sandboxes(
    client_with_account: mt.MailtrapClient,
) -> None:
    responses.get(SANDBOXES_URL, json=[])
    with pytest.warns(DeprecationWarning, match="testing_api"):
        testing_api = client_with_account.testing_api

    with pytest.warns(
        DeprecationWarning, match=r"inboxes is deprecated.*sandboxes"
    ) as record:
        api = testing_api.inboxes

    assert isinstance(api, InboxesApi)
    assert len(record) == 1
    assert api.get_list() == []
    assert len(responses.calls) == 1


def test_sending_domains_api_is_deprecated_alias_of_domains_api(
    client_with_account: mt.MailtrapClient,
) -> None:
    with pytest.warns(
        DeprecationWarning, match=r"sending_domains_api is deprecated.*domains_api"
    ) as record:
        api = client_with_account.sending_domains_api

    assert isinstance(api, SendingDomainsBaseApi)
    assert len(record) == 1
    assert record[0].filename == __file__


@responses.activate
def test_sending_domains_is_deprecated_alias_of_domains(
    client_with_account: mt.MailtrapClient,
) -> None:
    responses.get(DOMAINS_URL, json={"data": []})
    with pytest.warns(DeprecationWarning, match="sending_domains_api"):
        sending_domains_api = client_with_account.sending_domains_api

    with pytest.warns(
        DeprecationWarning, match=r"sending_domains is deprecated.*domains"
    ) as record:
        api = sending_domains_api.sending_domains

    assert isinstance(api, SendingDomainsApi)
    assert len(record) == 1
    assert api.get_list() == []
    assert len(responses.calls) == 1


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


def test_client_accepts_same_inbox_id_and_sandbox_id_of_different_types() -> None:
    with pytest.warns(DeprecationWarning, match="inbox_id"):
        client = mt.MailtrapClient(
            token="fake_token",
            sandbox=True,
            inbox_id=12345,  # type: ignore[arg-type]
            sandbox_id="12345",
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
