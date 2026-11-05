from typing import Optional

from mailtrap._deprecation import build_without_warning
from mailtrap._deprecation import warn_deprecated
from mailtrap.api.resources.inboxes import InboxesApi
from mailtrap.api.sandbox import SandboxApi
from mailtrap.http import HttpClient


class TestingApi(SandboxApi):
    """
    .. deprecated::
        Use :class:`mailtrap.api.sandbox.SandboxApi` instead.
    """

    def __init__(
        self, client: HttpClient, account_id: str, inbox_id: Optional[str] = None
    ) -> None:
        warn_deprecated("TestingApi", "SandboxApi")
        super().__init__(client=client, account_id=account_id)

    @property
    def inboxes(self) -> InboxesApi:
        """
        .. deprecated::
            Use :attr:`sandboxes` instead.
        """
        warn_deprecated("TestingApi.inboxes", "SandboxApi.sandboxes")
        return build_without_warning(
            InboxesApi, client=self._client, account_id=self._account_id
        )
