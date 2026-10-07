from typing import Optional

from mailtrap.http import HttpClient
from mailtrap.models.common import DeletedObject
from mailtrap.models.inbound import CreateInboundForwardRuleParams
from mailtrap.models.inbound import InboundForwardRule
from mailtrap.models.inbound import InboundForwardRuleResponse
from mailtrap.models.inbound import InboundForwardRulesListResponse
from mailtrap.models.inbound import UpdateInboundForwardRuleParams


class InboundForwardRulesApi:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def get_list(self, inbox_id: int) -> list[InboundForwardRule]:
        """Get all forward rules of an inbox."""
        response = self._client.get(self._api_path(inbox_id))
        return InboundForwardRulesListResponse(**response).data

    def get_by_id(self, inbox_id: int, forward_rule_id: int) -> InboundForwardRule:
        """Get a forward rule by ID."""
        response = self._client.get(self._api_path(inbox_id, forward_rule_id))
        return InboundForwardRuleResponse(**response).data

    def create(
        self, inbox_id: int, params: CreateInboundForwardRuleParams
    ) -> InboundForwardRule:
        """Create a forward rule on an inbox."""
        response = self._client.post(self._api_path(inbox_id), json=params.api_data)
        return InboundForwardRuleResponse(**response).data

    def update(
        self,
        inbox_id: int,
        forward_rule_id: int,
        params: UpdateInboundForwardRuleParams,
    ) -> InboundForwardRule:
        """Update a forward rule by ID."""
        response = self._client.patch(
            self._api_path(inbox_id, forward_rule_id), json=params.api_data
        )
        return InboundForwardRuleResponse(**response).data

    def delete(self, inbox_id: int, forward_rule_id: int) -> DeletedObject:
        """Delete a forward rule by ID."""
        self._client.delete(self._api_path(inbox_id, forward_rule_id))
        return DeletedObject(forward_rule_id)

    def _api_path(self, inbox_id: int, forward_rule_id: Optional[int] = None) -> str:
        path = f"/api/inbound/inboxes/{inbox_id}/forward_rules"
        if forward_rule_id:
            return f"{path}/{forward_rule_id}"
        return path
