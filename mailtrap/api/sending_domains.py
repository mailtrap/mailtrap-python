from mailtrap._deprecation import warn_deprecated
from mailtrap.api.domains import DomainsBaseApi
from mailtrap.api.resources.domains import DomainsApi


class SendingDomainsBaseApi(DomainsBaseApi):
    """
    .. deprecated::
        Use :class:`mailtrap.api.domains.DomainsBaseApi` instead.
    """

    @property
    def sending_domains(self) -> DomainsApi:
        """
        .. deprecated::
            Use :attr:`domains` instead.
        """
        warn_deprecated("SendingDomainsBaseApi.sending_domains", "DomainsBaseApi.domains")
        return self.domains
