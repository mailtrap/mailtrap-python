from mailtrap.api.resources.inbound_folders import InboundFoldersApi
from mailtrap.api.resources.inbound_forward_rules import InboundForwardRulesApi
from mailtrap.api.resources.inbound_inboxes import InboundInboxesApi
from mailtrap.api.resources.inbound_messages import InboundMessagesApi
from mailtrap.api.resources.inbound_threads import InboundThreadsApi
from mailtrap.http import HttpClient


class InboundBaseApi:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    @property
    def folders(self) -> InboundFoldersApi:
        return InboundFoldersApi(client=self._client)

    @property
    def inboxes(self) -> InboundInboxesApi:
        return InboundInboxesApi(client=self._client)

    @property
    def messages(self) -> InboundMessagesApi:
        return InboundMessagesApi(client=self._client)

    @property
    def threads(self) -> InboundThreadsApi:
        return InboundThreadsApi(client=self._client)

    @property
    def forward_rules(self) -> InboundForwardRulesApi:
        return InboundForwardRulesApi(client=self._client)
