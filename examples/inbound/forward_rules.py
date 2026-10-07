import os

import mailtrap as mt
from mailtrap.models.common import DeletedObject
from mailtrap.models.inbound import InboundForwardRule

API_KEY = os.environ["MAILTRAP_API_KEY"]
INBOX_ID = int(os.environ["MAILTRAP_INBOUND_INBOX_ID"])

client = mt.MailtrapClient(token=API_KEY)
forward_rules_api = client.inbound_api.forward_rules


def list_forward_rules(inbox_id: int) -> list[InboundForwardRule]:
    return forward_rules_api.get_list(inbox_id)


def get_forward_rule(inbox_id: int, forward_rule_id: int) -> InboundForwardRule:
    return forward_rules_api.get_by_id(inbox_id, forward_rule_id)


def create_forward_rule(inbox_id: int) -> InboundForwardRule:
    return forward_rules_api.create(
        inbox_id,
        mt.CreateInboundForwardRuleParams(
            name="Copy billing mail to finance",
            conditions=[
                mt.InboundForwardRuleConditionParams(
                    match_type="sender",
                    operator="ends_with",
                    value="@billing.example.com",
                ),
            ],
            destinations=[mt.InboundForwardRuleDestination(email="finance@example.com")],
        ),
    )


def update_forward_rule(inbox_id: int, forward_rule_id: int) -> InboundForwardRule:
    return forward_rules_api.update(
        inbox_id,
        forward_rule_id,
        mt.UpdateInboundForwardRuleParams(
            destinations=[
                mt.InboundForwardRuleDestination(email="finance@example.com"),
                mt.InboundForwardRuleDestination(email="accounting@example.com"),
            ],
        ),
    )


def delete_forward_rule(inbox_id: int, forward_rule_id: int) -> DeletedObject:
    return forward_rules_api.delete(inbox_id, forward_rule_id)


if __name__ == "__main__":
    rule = create_forward_rule(INBOX_ID)
    print(rule)

    print(list_forward_rules(INBOX_ID))
    print(get_forward_rule(INBOX_ID, rule.id))
    print(update_forward_rule(INBOX_ID, rule.id))
    print(delete_forward_rule(INBOX_ID, rule.id))
