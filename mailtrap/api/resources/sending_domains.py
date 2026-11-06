from mailtrap._deprecation import warn_deprecated
from mailtrap.api.resources.domains import DomainsApi
from mailtrap.http import HttpClient


class SendingDomainsApi(DomainsApi):
    """
    .. deprecated::
        Use :class:`mailtrap.api.resources.domains.DomainsApi` instead.
    """

    def __init__(self, client: HttpClient, account_id: str) -> None:
        warn_deprecated("SendingDomainsApi", "DomainsApi")
        super().__init__(client=client, account_id=account_id)
