import warnings

from mailtrap.api.resources.templates import TemplatesApi
from mailtrap.http import HttpClient


class EmailTemplatesApi:
    def __init__(self, client: HttpClient, account_id: str) -> None:
        self._account_id = account_id
        self._client = client

    @property
    def templates(self) -> TemplatesApi:
        """
        Deprecated: use ``MailtrapClient.templates_api.templates``, which
        serves the paginated ``/api/templates`` endpoints.
        """
        warnings.warn(
            "EmailTemplatesApi is deprecated; use MailtrapClient.templates_api.templates",
            DeprecationWarning,
            stacklevel=2,
        )
        return TemplatesApi(account_id=self._account_id, client=self._client)
