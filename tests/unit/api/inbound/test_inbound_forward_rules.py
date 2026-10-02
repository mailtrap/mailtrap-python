import json
from typing import Any

import pytest
import responses

from mailtrap.api.resources.inbound_forward_rules import InboundForwardRulesApi
from mailtrap.config import GENERAL_HOST
from mailtrap.exceptions import APIError
from mailtrap.http import HttpClient
from mailtrap.models.common import DeletedObject
from mailtrap.models.inbound import CreateInboundForwardRuleParams
from mailtrap.models.inbound import InboundForwardRule
from mailtrap.models.inbound import InboundForwardRuleConditionParams
from mailtrap.models.inbound import InboundForwardRuleDestination
from mailtrap.models.inbound import UpdateInboundForwardRuleParams
from tests import conftest

INBOX_ID = 9
FORWARD_RULE_ID = 7
BASE_URL = f"https://{GENERAL_HOST}/api/inbound/inboxes/{INBOX_ID}/forward_rules"

ERROR_CASES = [
    (
        conftest.UNAUTHORIZED_STATUS_CODE,
        conftest.UNAUTHORIZED_RESPONSE,
        conftest.UNAUTHORIZED_ERROR_MESSAGE,
    ),
    (
        conftest.NOT_FOUND_STATUS_CODE,
        conftest.NOT_FOUND_RESPONSE,
        conftest.NOT_FOUND_ERROR_MESSAGE,
    ),
]

VALIDATION_ERROR_CASES = [
    *ERROR_CASES,
    (
        conftest.VALIDATION_ERRORS_STATUS_CODE,
        {"errors": {"conditions.value": ["can't be blank"]}},
        "conditions.value",
    ),
]


def _rule_json(**overrides: Any) -> dict[str, Any]:
    rule: dict[str, Any] = {
        "id": FORWARD_RULE_ID,
        "name": "Copy billing mail to finance",
        "created_at": "2026-05-08T10:30:00.000Z",
        "updated_at": "2026-05-08T10:30:00.000Z",
        "conditions": [
            {
                "match_type": "sender",
                "operator": "ends_with",
                "value": "@billing.example.com",
                "header_key": None,
            }
        ],
        "destinations": [{"email": "finance@example.com"}],
    }
    rule.update(overrides)
    return rule


@pytest.fixture
def forward_rules_api() -> InboundForwardRulesApi:
    return InboundForwardRulesApi(client=HttpClient(GENERAL_HOST))


class TestInboundForwardRulesApi:

    @responses.activate
    def test_get_list_should_return_rules(
        self, forward_rules_api: InboundForwardRulesApi
    ) -> None:
        responses.get(
            BASE_URL,
            json={
                "data": [
                    _rule_json(),
                    _rule_json(id=8, name="Archive", conditions=[]),
                ]
            },
            status=200,
        )

        rules = forward_rules_api.get_list(INBOX_ID)

        assert all(isinstance(r, InboundForwardRule) for r in rules)
        assert [r.id for r in rules] == [FORWARD_RULE_ID, 8]
        assert rules[0].conditions[0].operator == "ends_with"
        assert rules[0].conditions[0].header_key is None
        assert rules[0].destinations[0].email == "finance@example.com"
        assert rules[1].conditions == []

    @responses.activate
    def test_get_list_should_return_empty_list(
        self, forward_rules_api: InboundForwardRulesApi
    ) -> None:
        responses.get(BASE_URL, json={"data": []}, status=200)

        assert forward_rules_api.get_list(INBOX_ID) == []

    @pytest.mark.parametrize(
        "status_code,response_json,expected_error_message", ERROR_CASES
    )
    @responses.activate
    def test_get_list_should_raise_api_errors(
        self,
        forward_rules_api: InboundForwardRulesApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.get(BASE_URL, status=status_code, json=response_json)

        with pytest.raises(APIError) as exc_info:
            forward_rules_api.get_list(INBOX_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_by_id_should_return_rule(
        self, forward_rules_api: InboundForwardRulesApi
    ) -> None:
        responses.get(
            f"{BASE_URL}/{FORWARD_RULE_ID}",
            json={
                "data": _rule_json(
                    conditions=[
                        {
                            "match_type": "header",
                            "operator": "equal",
                            "value": "high",
                            "header_key": "X-Priority-Level",
                        }
                    ]
                )
            },
            status=200,
        )

        rule = forward_rules_api.get_by_id(INBOX_ID, FORWARD_RULE_ID)

        assert isinstance(rule, InboundForwardRule)
        assert rule.id == FORWARD_RULE_ID
        assert rule.conditions[0].match_type == "header"
        assert rule.conditions[0].header_key == "X-Priority-Level"

    @pytest.mark.parametrize(
        "status_code,response_json,expected_error_message", ERROR_CASES
    )
    @responses.activate
    def test_get_by_id_should_raise_api_errors(
        self,
        forward_rules_api: InboundForwardRulesApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.get(
            f"{BASE_URL}/{FORWARD_RULE_ID}", status=status_code, json=response_json
        )

        with pytest.raises(APIError) as exc_info:
            forward_rules_api.get_by_id(INBOX_ID, FORWARD_RULE_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_create_should_send_flat_body_and_return_rule(
        self, forward_rules_api: InboundForwardRulesApi
    ) -> None:
        responses.post(BASE_URL, json={"data": _rule_json()}, status=201)

        rule = forward_rules_api.create(
            INBOX_ID,
            CreateInboundForwardRuleParams(
                name="Copy billing mail to finance",
                conditions=[
                    InboundForwardRuleConditionParams(
                        match_type="sender",
                        operator="ends_with",
                        value="@billing.example.com",
                    )
                ],
                destinations=[InboundForwardRuleDestination(email="finance@example.com")],
            ),
        )

        assert isinstance(rule, InboundForwardRule)
        assert rule.id == FORWARD_RULE_ID
        assert json.loads(responses.calls[-1].request.body) == {
            "name": "Copy billing mail to finance",
            "conditions": [
                {
                    "match_type": "sender",
                    "operator": "ends_with",
                    "value": "@billing.example.com",
                }
            ],
            "destinations": [{"email": "finance@example.com"}],
        }

    @responses.activate
    def test_create_should_send_only_name_when_lists_omitted(
        self, forward_rules_api: InboundForwardRulesApi
    ) -> None:
        responses.post(
            BASE_URL,
            json={"data": _rule_json(conditions=[], destinations=[])},
            status=201,
        )

        forward_rules_api.create(
            INBOX_ID, CreateInboundForwardRuleParams(name="Copy billing mail to finance")
        )

        assert json.loads(responses.calls[-1].request.body) == {
            "name": "Copy billing mail to finance"
        }

    @pytest.mark.parametrize(
        "status_code,response_json,expected_error_message", VALIDATION_ERROR_CASES
    )
    @responses.activate
    def test_create_should_raise_api_errors(
        self,
        forward_rules_api: InboundForwardRulesApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.post(BASE_URL, status=status_code, json=response_json)

        with pytest.raises(APIError) as exc_info:
            forward_rules_api.create(INBOX_ID, CreateInboundForwardRuleParams(name="x"))

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_update_should_send_only_given_fields(
        self, forward_rules_api: InboundForwardRulesApi
    ) -> None:
        responses.patch(
            f"{BASE_URL}/{FORWARD_RULE_ID}",
            json={
                "data": _rule_json(
                    destinations=[
                        {"email": "finance@example.com"},
                        {"email": "accounting@example.com"},
                    ]
                )
            },
            status=200,
        )

        rule = forward_rules_api.update(
            INBOX_ID,
            FORWARD_RULE_ID,
            UpdateInboundForwardRuleParams(
                destinations=[
                    InboundForwardRuleDestination(email="finance@example.com"),
                    InboundForwardRuleDestination(email="accounting@example.com"),
                ]
            ),
        )

        assert isinstance(rule, InboundForwardRule)
        assert len(rule.destinations) == 2
        assert json.loads(responses.calls[-1].request.body) == {
            "destinations": [
                {"email": "finance@example.com"},
                {"email": "accounting@example.com"},
            ]
        }

    @responses.activate
    def test_update_should_send_empty_lists_to_clear_sets(
        self, forward_rules_api: InboundForwardRulesApi
    ) -> None:
        responses.patch(
            f"{BASE_URL}/{FORWARD_RULE_ID}",
            json={"data": _rule_json(conditions=[], destinations=[])},
            status=200,
        )

        rule = forward_rules_api.update(
            INBOX_ID,
            FORWARD_RULE_ID,
            UpdateInboundForwardRuleParams(conditions=[], destinations=[]),
        )

        assert rule.conditions == []
        assert json.loads(responses.calls[-1].request.body) == {
            "conditions": [],
            "destinations": [],
        }

    @pytest.mark.parametrize(
        "status_code,response_json,expected_error_message", VALIDATION_ERROR_CASES
    )
    @responses.activate
    def test_update_should_raise_api_errors(
        self,
        forward_rules_api: InboundForwardRulesApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.patch(
            f"{BASE_URL}/{FORWARD_RULE_ID}", status=status_code, json=response_json
        )

        with pytest.raises(APIError) as exc_info:
            forward_rules_api.update(
                INBOX_ID, FORWARD_RULE_ID, UpdateInboundForwardRuleParams(name="x")
            )

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_delete_should_return_deleted_object(
        self, forward_rules_api: InboundForwardRulesApi
    ) -> None:
        responses.delete(f"{BASE_URL}/{FORWARD_RULE_ID}", status=204)

        deleted = forward_rules_api.delete(INBOX_ID, FORWARD_RULE_ID)

        assert isinstance(deleted, DeletedObject)
        assert deleted.id == FORWARD_RULE_ID

    @pytest.mark.parametrize(
        "status_code,response_json,expected_error_message", ERROR_CASES
    )
    @responses.activate
    def test_delete_should_raise_api_errors(
        self,
        forward_rules_api: InboundForwardRulesApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.delete(
            f"{BASE_URL}/{FORWARD_RULE_ID}", status=status_code, json=response_json
        )

        with pytest.raises(APIError) as exc_info:
            forward_rules_api.delete(INBOX_ID, FORWARD_RULE_ID)

        assert expected_error_message in str(exc_info.value)
