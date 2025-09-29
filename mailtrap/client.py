import warnings
from typing import Optional
from typing import Union
from typing import cast

from pydantic import TypeAdapter

from mailtrap.api.contacts import ContactsBaseApi
from mailtrap.api.sending import SendingApi
from mailtrap.api.suppressions import SuppressionsBaseApi
from mailtrap.api.templates import EmailTemplatesApi
from mailtrap.api.testing import TestingApi
from mailtrap.config import BULK_HOST
from mailtrap.config import GENERAL_HOST
from mailtrap.config import SANDBOX_HOST
from mailtrap.config import SENDING_HOST
from mailtrap.exceptions import ClientConfigurationError
from mailtrap.http import HttpClient
from mailtrap.models.mail import BaseMail
from mailtrap.models.mail import BatchSendResponse
from mailtrap.models.mail import SendingMailResponse
from mailtrap.models.mail.batch_mail import BatchSendEmailParams

SEND_ENDPOINT_RESPONSE = dict[str, Union[bool, list[str]]]
BATCH_SEND_ENDPOINT_RESPONSE = dict[
    str, Union[bool, list[str], list[dict[str, Union[bool, list[str]]]]]
]


class MailtrapClient:
    DEFAULT_HOST = SENDING_HOST
    DEFAULT_PORT = 443
    BULK_HOST = BULK_HOST
    SANDBOX_HOST = SANDBOX_HOST

    def __init__(
        self,
        token: str,
        api_host: Optional[str] = None,
        api_port: int = DEFAULT_PORT,
        bulk: bool = False,
        sandbox: bool = False,
        account_id: Optional[str] = None,
        inbox_id: Optional[str] = None,
    ) -> None:
        self.token = token
        self.api_host = api_host
        self.api_port = api_port
        self.bulk = bulk
        self.sandbox = sandbox
        self.account_id = account_id
        self.inbox_id = inbox_id

        self._validate_itself()

    @property
    def testing_api(self) -> TestingApi:
        self._validate_account_id()
        return TestingApi(
            account_id=cast(str, self.account_id),
            inbox_id=self.inbox_id,
            client=HttpClient(host=GENERAL_HOST, headers=self.headers),
        )

    @property
    def email_templates_api(self) -> EmailTemplatesApi:
        self._validate_account_id()
        return EmailTemplatesApi(
            account_id=cast(str, self.account_id),
            client=HttpClient(host=GENERAL_HOST, headers=self.headers),
        )

    @property
    def contacts_api(self) -> ContactsBaseApi:
        self._validate_account_id()
        return ContactsBaseApi(
            account_id=cast(str, self.account_id),
            client=HttpClient(host=GENERAL_HOST, headers=self.headers),
        )

    @property
    def suppressions_api(self) -> SuppressionsBaseApi:
        self._validate_account_id()
        return SuppressionsBaseApi(
            account_id=cast(str, self.account_id),
            client=HttpClient(host=GENERAL_HOST, headers=self.headers),
        )

    @property
    def sending_api(self) -> SendingApi:
        http_client = HttpClient(host=self._sending_api_host, headers=self.headers)
        return SendingApi(client=http_client, inbox_id=self.inbox_id)

    def send(self, mail: BaseMail) -> SEND_ENDPOINT_RESPONSE:
        sending_response = self.sending_api.send(mail)
        return cast(
            SEND_ENDPOINT_RESPONSE,
            TypeAdapter(SendingMailResponse).dump_python(sending_response),
        )

    def batch_send(self, mail: BatchSendEmailParams) -> BATCH_SEND_ENDPOINT_RESPONSE:
        batch_sending_response = self.sending_api.batch_send(mail)
        return cast(
            BATCH_SEND_ENDPOINT_RESPONSE,
            TypeAdapter(BatchSendResponse).dump_python(batch_sending_response),
        )

    @property
    def base_url(self) -> str:
        warnings.warn(
            "base_url is deprecated and will be removed in a future release.",
            DeprecationWarning,
            stacklevel=2,
        )
        return f"https://{self._sending_api_host.rstrip('/')}:{self.api_port}"

    @property
    def api_send_url(self) -> str:
        warnings.warn(
            "api_send_url is deprecated and will be removed in a future release.",
            DeprecationWarning,
            stacklevel=2,
        )
        url = f"{self.base_url}/api/send"
        if self.sandbox and self.inbox_id:
            return f"{url}/{self.inbox_id}"
        return url

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "User-Agent": (
                "mailtrap-python (https://github.com/railsware/mailtrap-python)"
            ),
        }

    @property
    def _sending_api_host(self) -> str:
        if self.api_host:
            return self.api_host
        if self.sandbox:
            return SANDBOX_HOST
        if self.bulk:
            return BULK_HOST
        return SENDING_HOST

    def _validate_account_id(self) -> None:
        if not self.account_id:
            raise ClientConfigurationError("`account_id` is required for Testing API")

    def _validate_itself(self) -> None:
        if self.sandbox and not self.inbox_id:
            raise ClientConfigurationError("`inbox_id` is required for sandbox mode")

        if not self.sandbox and self.inbox_id:
            raise ClientConfigurationError(
                "`inbox_id` is not allowed in non-sandbox mode"
            )

        if self.bulk and self.sandbox:
            raise ClientConfigurationError("bulk mode is not allowed in sandbox mode")
