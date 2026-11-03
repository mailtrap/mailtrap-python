from typing import Optional

from mailtrap._deprecation import warn_deprecated
from mailtrap.api.resources.sandboxes import SandboxesApi
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
        super().__init__(client=client, account_id=account_id)

    @property
    def inboxes(self) -> SandboxesApi:
        """
        .. deprecated::
            Use :attr:`sandboxes` instead.
        """
        warn_deprecated("TestingApi.inboxes", "SandboxApi.sandboxes")
        return self.sandboxes
