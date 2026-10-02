import pytest

from mailtrap.models.inbound import CreateInboundFolderParams
from mailtrap.models.inbound import CreateInboundForwardRuleParams
from mailtrap.models.inbound import CreateInboundInboxParams
from mailtrap.models.inbound import ForwardInboundMessageParams
from mailtrap.models.inbound import InboundForwardRuleConditionParams
from mailtrap.models.inbound import InboundForwardRuleDestination
from mailtrap.models.inbound import InboundMessage
from mailtrap.models.inbound import InboundThread
from mailtrap.models.inbound import ReplyInboundMessageParams
from mailtrap.models.inbound import UpdateInboundForwardRuleParams
from mailtrap.models.mail.address import Address


class TestInboundParams:
    def test_create_folder_api_data(self) -> None:
        assert CreateInboundFolderParams(name="Support").api_data == {"name": "Support"}

    def test_create_inbox_includes_domain_id(self) -> None:
        params = CreateInboundInboxParams(name="Tickets", domain_id=3)
        assert params.api_data == {"name": "Tickets", "domain_id": 3}

    def test_create_inbox_omits_domain_id_when_none(self) -> None:
        assert CreateInboundInboxParams(name="Tickets").api_data == {"name": "Tickets"}

    def test_reply_serializes_sender_as_from_and_excludes_none(self) -> None:
        params = ReplyInboundMessageParams(
            sender=Address(email="me@example.com"), text="Thanks!"
        )
        assert params.api_data == {
            "from": {"email": "me@example.com"},
            "text": "Thanks!",
        }

    def test_forward_serializes_recipients(self) -> None:
        params = ForwardInboundMessageParams(
            to=[Address(email="colleague@example.com")], text="FYI"
        )
        assert params.api_data == {
            "to": [{"email": "colleague@example.com"}],
            "text": "FYI",
        }

    def test_forward_requires_at_least_one_recipient(self) -> None:
        with pytest.raises(ValueError):
            ForwardInboundMessageParams(to=[])


class TestInboundResponseModels:
    def test_message_parses_from_alias_and_attachments(self) -> None:
        message = InboundMessage(
            **{
                "id": "m1",
                "inbox_id": 9,
                "from": "customer@example.com",
                "received_at": "2026-01-15T10:30:00Z",
                "attachments": [{"attachment_id": "a1", "download_url": "https://x/a1"}],
            }
        )
        assert message.from_ == "customer@example.com"
        assert message.attachments[0].download_url == "https://x/a1"
        assert message.to == []
        assert message.forwards == []

    def test_thread_parses_nested_messages(self) -> None:
        thread = InboundThread(
            **{
                "id": "t1",
                "message_count": 1,
                "size": 10,
                "first_message_at": "2026-01-15T10:00:00Z",
                "last_activity_at": "2026-01-15T10:00:00Z",
                "messages": [
                    {"visibility_status": "placeholder", "direction": "outbound"}
                ],
            }
        )
        assert thread.messages[0].visibility_status == "placeholder"
        assert thread.messages[0].from_ is None


class TestInboundForwardRuleParams:
    def test_create_serializes_conditions_and_destinations(self) -> None:
        params = CreateInboundForwardRuleParams(
            name="Urgent",
            conditions=[
                InboundForwardRuleConditionParams(
                    match_type="header",
                    operator="not_empty",
                    header_key="X-Priority-Level",
                )
            ],
            destinations=[InboundForwardRuleDestination(email="oncall@example.com")],
        )
        assert params.api_data == {
            "name": "Urgent",
            "conditions": [
                {
                    "match_type": "header",
                    "operator": "not_empty",
                    "header_key": "X-Priority-Level",
                }
            ],
            "destinations": [{"email": "oncall@example.com"}],
        }

    def test_update_omits_unset_fields(self) -> None:
        assert UpdateInboundForwardRuleParams(name="Renamed").api_data == {
            "name": "Renamed"
        }
        assert UpdateInboundForwardRuleParams().api_data == {}

    def test_update_keeps_empty_lists(self) -> None:
        params = UpdateInboundForwardRuleParams(conditions=[], destinations=[])
        assert params.api_data == {"conditions": [], "destinations": []}

    @pytest.mark.parametrize(
        "match_type,operator", [("domain", "equal"), ("sender", "matches")]
    )
    def test_condition_rejects_unknown_enum_values(
        self, match_type: str, operator: str
    ) -> None:
        with pytest.raises(ValueError):
            InboundForwardRuleConditionParams(
                match_type=match_type,  # type: ignore[arg-type]
                operator=operator,  # type: ignore[arg-type]
                value="x",
            )
