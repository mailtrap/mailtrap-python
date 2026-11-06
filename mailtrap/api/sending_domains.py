from mailtrap._deprecation import build_without_warning
from mailtrap._deprecation import warn_deprecated
from mailtrap.api.domains import DomainsBaseApi
from mailtrap.api.resources.sending_domains import SendingDomainsApi
from mailtrap.http import HttpClient


class SendingDomainsBaseApi(DomainsBaseApi):
    """
    .. deprecated::
        Use :class:`mailtrap.api.domains.DomainsBaseApi` instead.
    """

    def __init__(self, client: HttpClient, account_id: str) -> None:
        warn_deprecated("SendingDomainsBaseApi", "DomainsBaseApi")
        super().__init__(client=client, account_id=account_id)

    @property
    def sending_domains(self) -> SendingDomainsApi:
        """
        .. deprecated::
            Use :attr:`domains` instead.
        """
        warn_deprecated("SendingDomainsBaseApi.sending_domains", "DomainsBaseApi.domains")
        return build_without_warning(
            SendingDomainsApi, client=self._client, account_id=self._account_id
        )
