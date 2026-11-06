from mailtrap._deprecation import warn_deprecated
from mailtrap.api.resources.sandboxes import SandboxesApi
from mailtrap.http import HttpClient


class InboxesApi(SandboxesApi):
    """
    .. deprecated::
        Use :class:`mailtrap.api.resources.sandboxes.SandboxesApi` instead.
    """

    def __init__(self, client: HttpClient, account_id: str) -> None:
        warn_deprecated("InboxesApi", "SandboxesApi")
        super().__init__(client=client, account_id=account_id)
