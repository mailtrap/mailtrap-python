import json
from typing import Any

import pytest
import responses

from mailtrap.api.resources.domains import DomainsApi
from mailtrap.config import GENERAL_HOST
from mailtrap.exceptions import APIError
from mailtrap.http import HttpClient
from mailtrap.models.common import DeletedObject
from mailtrap.models.domains import CreateDomainParams
from mailtrap.models.domains import Domain
from mailtrap.models.domains import SendSetupInstructionsParams
from mailtrap.models.domains import SendSetupInstructionsResponse
from mailtrap.models.domains import UpdateDomainParams
from tests import conftest

ACCOUNT_ID = "1234567"
DOMAIN_ID = 432
BASE_SENDING_DOMAINS_URL = (
    f"https://{GENERAL_HOST}/api/accounts/{ACCOUNT_ID}/sending_domains"
)


@pytest.fixture
def domains_api() -> DomainsApi:
    return DomainsApi(account_id=ACCOUNT_ID, client=HttpClient(GENERAL_HOST))


@pytest.fixture
def sample_domain_dict() -> dict[str, Any]:
    return {
        "id": DOMAIN_ID,
        "domain_name": "example.com",
        "demo": False,
        "compliance_status": "verified",
        "dns_verified": True,
        "open_tracking_enabled": True,
        "click_tracking_enabled": True,
        "auto_unsubscribe_link_enabled": False,
        "custom_domain_tracking_enabled": False,
        "health_alerts_enabled": True,
        "critical_alerts_enabled": True,
        "permissions": {
            "can_read": True,
            "can_update": True,
            "can_destroy": True,
        },
        "alert_recipient_email": "admin@example.com",
        "dns_verified_at": "2024-12-26T09:40:44.161Z",
        "dns_records": [
            {
                "key": "dkim",
                "domain": "example.com",
                "type": "CNAME",
                "value": "example.com.mailtrap.io",
                "status": "verified",
                "name": "mail",
            }
        ],
    }


class TestDomainsApi:

    @pytest.mark.parametrize(
        "status_code,response_json,expected_error_message",
        [
            (
                conftest.UNAUTHORIZED_STATUS_CODE,
                conftest.UNAUTHORIZED_RESPONSE,
                conftest.UNAUTHORIZED_ERROR_MESSAGE,
            ),
            (
                conftest.FORBIDDEN_STATUS_CODE,
                conftest.FORBIDDEN_RESPONSE,
                conftest.FORBIDDEN_ERROR_MESSAGE,
            ),
        ],
    )
    @responses.activate
    def test_get_domains_should_raise_api_errors(
        self,
        domains_api: DomainsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.get(
            BASE_SENDING_DOMAINS_URL,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            domains_api.get_list()

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_domains_should_return_domains_list(
        self, domains_api: DomainsApi, sample_domain_dict: dict
    ) -> None:
        responses.get(
            BASE_SENDING_DOMAINS_URL,
            json={"data": [sample_domain_dict]},
            status=200,
        )

        domains = domains_api.get_list()

        assert isinstance(domains, list)
        assert all(isinstance(d, Domain) for d in domains)
        assert domains[0].id == DOMAIN_ID
        assert domains[0].domain_name == "example.com"
        assert domains[0].dns_verified is True

    @pytest.mark.parametrize(
        "status_code,response_json,expected_error_message",
        [
            (
                conftest.UNAUTHORIZED_STATUS_CODE,
                conftest.UNAUTHORIZED_RESPONSE,
                conftest.UNAUTHORIZED_ERROR_MESSAGE,
            ),
            (
                conftest.FORBIDDEN_STATUS_CODE,
                conftest.FORBIDDEN_RESPONSE,
                conftest.FORBIDDEN_ERROR_MESSAGE,
            ),
            (
                conftest.NOT_FOUND_STATUS_CODE,
                conftest.NOT_FOUND_RESPONSE,
                conftest.NOT_FOUND_ERROR_MESSAGE,
            ),
        ],
    )
    @responses.activate
    def test_get_domain_by_id_should_raise_api_errors(
        self,
        domains_api: DomainsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.get(
            f"{BASE_SENDING_DOMAINS_URL}/{DOMAIN_ID}",
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            domains_api.get_by_id(DOMAIN_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_domain_by_id_should_return_domain(
        self, domains_api: DomainsApi, sample_domain_dict: dict
    ) -> None:
        responses.get(
            f"{BASE_SENDING_DOMAINS_URL}/{DOMAIN_ID}",
            json=sample_domain_dict,
            status=200,
        )

        domain = domains_api.get_by_id(DOMAIN_ID)

        assert isinstance(domain, Domain)
        assert domain.id == DOMAIN_ID
        assert domain.domain_name == "example.com"
        assert domain.compliance_status == "verified"
        assert domain.dns_verified is True

    @pytest.mark.parametrize(
        "status_code,response_json,expected_error_message",
        [
            (
                conftest.UNAUTHORIZED_STATUS_CODE,
                conftest.UNAUTHORIZED_RESPONSE,
                conftest.UNAUTHORIZED_ERROR_MESSAGE,
            ),
            (
                conftest.FORBIDDEN_STATUS_CODE,
                conftest.FORBIDDEN_RESPONSE,
                conftest.FORBIDDEN_ERROR_MESSAGE,
            ),
            (
                conftest.VALIDATION_ERRORS_STATUS_CODE,
                {
                    "errors": {
                        "base": ["Validation failed: Domain name has already been taken"]
                    }
                },
                "Validation failed",
            ),
        ],
    )
    @responses.activate
    def test_create_domain_should_raise_api_errors(
        self,
        domains_api: DomainsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.post(
            BASE_SENDING_DOMAINS_URL,
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            params = CreateDomainParams(domain_name="example.com")
            domains_api.create(params)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_create_domain_should_return_created_domain(
        self, domains_api: DomainsApi, sample_domain_dict: dict
    ) -> None:
        responses.post(
            BASE_SENDING_DOMAINS_URL,
            json=sample_domain_dict,
            status=200,
        )

        params = CreateDomainParams(domain_name="example.com")
        domain = domains_api.create(params)

        assert isinstance(domain, Domain)
        assert domain.id == DOMAIN_ID
        assert domain.domain_name == "example.com"

    @pytest.mark.parametrize(
        "status_code,response_json,expected_error_message",
        [
            (
                conftest.UNAUTHORIZED_STATUS_CODE,
                conftest.UNAUTHORIZED_RESPONSE,
                conftest.UNAUTHORIZED_ERROR_MESSAGE,
            ),
            (
                conftest.FORBIDDEN_STATUS_CODE,
                conftest.FORBIDDEN_RESPONSE,
                conftest.FORBIDDEN_ERROR_MESSAGE,
            ),
            (
                conftest.NOT_FOUND_STATUS_CODE,
                conftest.NOT_FOUND_RESPONSE,
                conftest.NOT_FOUND_ERROR_MESSAGE,
            ),
            (
                conftest.VALIDATION_ERRORS_STATUS_CODE,
                {"errors": "Tracking opt out is invalid"},
                "Tracking opt out is invalid",
            ),
            (
                conftest.INTERNAL_SERVER_ERROR_STATUS_CODE,
                conftest.INTERNAL_SERVER_ERROR_RESPONSE,
                conftest.INTERNAL_SERVER_ERROR_MESSAGE,
            ),
        ],
    )
    @responses.activate
    def test_update_domain_should_raise_api_errors(
        self,
        domains_api: DomainsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.patch(
            f"{BASE_SENDING_DOMAINS_URL}/{DOMAIN_ID}",
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            params = UpdateDomainParams(open_tracking_enabled=True)
            domains_api.update(DOMAIN_ID, params)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_update_domain_should_return_updated_domain(
        self, domains_api: DomainsApi, sample_domain_dict: dict
    ) -> None:
        sample_domain_dict["tracking_opt_out_enabled"] = True
        sample_domain_dict["auto_unsubscribe_link_enabled"] = False
        responses.patch(
            f"{BASE_SENDING_DOMAINS_URL}/{DOMAIN_ID}",
            json=sample_domain_dict,
            status=200,
        )

        params = UpdateDomainParams(
            open_tracking_enabled=True,
            click_tracking_enabled=True,
            tracking_opt_out_enabled=True,
            auto_unsubscribe_link_enabled=False,
            inbound_enabled=False,
        )
        domain = domains_api.update(DOMAIN_ID, params)

        assert isinstance(domain, Domain)
        assert domain.tracking_opt_out_enabled is True
        assert domain.auto_unsubscribe_link_enabled is False
        assert responses.calls[0].request.body is not None
        assert json.loads(responses.calls[0].request.body) == {
            "sending_domain": {
                "open_tracking_enabled": True,
                "click_tracking_enabled": True,
                "tracking_opt_out_enabled": True,
                "auto_unsubscribe_link_enabled": False,
                "inbound_enabled": False,
            }
        }

    @responses.activate
    def test_update_domain_should_send_only_supplied_fields(
        self, domains_api: DomainsApi, sample_domain_dict: dict
    ) -> None:
        responses.patch(
            f"{BASE_SENDING_DOMAINS_URL}/{DOMAIN_ID}",
            json=sample_domain_dict,
            status=200,
        )

        params = UpdateDomainParams(tracking_opt_out_enabled=True)
        domains_api.update(DOMAIN_ID, params)

        assert responses.calls[0].request.body is not None
        assert json.loads(responses.calls[0].request.body) == {
            "sending_domain": {"tracking_opt_out_enabled": True}
        }

    @pytest.mark.parametrize(
        "status_code,response_json,expected_error_message",
        [
            (
                conftest.UNAUTHORIZED_STATUS_CODE,
                conftest.UNAUTHORIZED_RESPONSE,
                conftest.UNAUTHORIZED_ERROR_MESSAGE,
            ),
            (
                conftest.FORBIDDEN_STATUS_CODE,
                conftest.FORBIDDEN_RESPONSE,
                conftest.FORBIDDEN_ERROR_MESSAGE,
            ),
            (
                conftest.NOT_FOUND_STATUS_CODE,
                conftest.NOT_FOUND_RESPONSE,
                conftest.NOT_FOUND_ERROR_MESSAGE,
            ),
            (
                conftest.INTERNAL_SERVER_ERROR_STATUS_CODE,
                conftest.INTERNAL_SERVER_ERROR_RESPONSE,
                conftest.INTERNAL_SERVER_ERROR_MESSAGE,
            ),
        ],
    )
    @responses.activate
    def test_delete_domain_should_raise_api_errors(
        self,
        domains_api: DomainsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.delete(
            f"{BASE_SENDING_DOMAINS_URL}/{DOMAIN_ID}",
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            domains_api.delete(DOMAIN_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_delete_domain_should_return_deleted_object(
        self, domains_api: DomainsApi
    ) -> None:
        responses.delete(
            f"{BASE_SENDING_DOMAINS_URL}/{DOMAIN_ID}",
            status=204,
        )

        deleted_domain = domains_api.delete(DOMAIN_ID)

        assert isinstance(deleted_domain, DeletedObject)
        assert deleted_domain.id == DOMAIN_ID

    @pytest.mark.parametrize(
        "status_code,response_json,expected_error_message",
        [
            (
                conftest.UNAUTHORIZED_STATUS_CODE,
                conftest.UNAUTHORIZED_RESPONSE,
                conftest.UNAUTHORIZED_ERROR_MESSAGE,
            ),
            (
                conftest.FORBIDDEN_STATUS_CODE,
                conftest.FORBIDDEN_RESPONSE,
                conftest.FORBIDDEN_ERROR_MESSAGE,
            ),
            (
                conftest.NOT_FOUND_STATUS_CODE,
                conftest.NOT_FOUND_RESPONSE,
                conftest.NOT_FOUND_ERROR_MESSAGE,
            ),
        ],
    )
    @responses.activate
    def test_send_setup_instructions_should_raise_api_errors(
        self,
        domains_api: DomainsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.post(
            f"{BASE_SENDING_DOMAINS_URL}/{DOMAIN_ID}/send_setup_instructions",
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            params = SendSetupInstructionsParams(email="admin@example.com")
            domains_api.send_setup_instructions(DOMAIN_ID, params)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_send_setup_instructions_should_return_success_response(
        self, domains_api: DomainsApi
    ) -> None:
        responses.post(
            f"{BASE_SENDING_DOMAINS_URL}/{DOMAIN_ID}/send_setup_instructions",
            status=204,
        )

        params = SendSetupInstructionsParams(email="admin@example.com")
        response = domains_api.send_setup_instructions(DOMAIN_ID, params)

        assert isinstance(response, SendSetupInstructionsResponse)
        assert response.message == "Instructions email has been sent successfully"
