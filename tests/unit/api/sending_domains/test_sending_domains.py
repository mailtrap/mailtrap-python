from typing import Any

import pytest
import responses

from mailtrap.api.resources.sending_domains import SendingDomainsApi
from mailtrap.config import GENERAL_HOST
from mailtrap.exceptions import APIError
from mailtrap.http import HttpClient
from mailtrap.models.common import DeletedObject
from mailtrap.models.sending_domains import CreateSendingDomainParams
from mailtrap.models.sending_domains import SendingDomain
from mailtrap.models.sending_domains import SendSetupInstructionsParams
from mailtrap.models.sending_domains import SendSetupInstructionsResponse
from tests import conftest

ACCOUNT_ID = "1234567"
DOMAIN_ID = 432
BASE_SENDING_DOMAINS_URL = (
    f"https://{GENERAL_HOST}/api/accounts/{ACCOUNT_ID}/sending_domains"
)


@pytest.fixture
def sending_domains_api() -> SendingDomainsApi:
    return SendingDomainsApi(account_id=ACCOUNT_ID, client=HttpClient(GENERAL_HOST))


@pytest.fixture
def sample_sending_domain_dict() -> dict[str, Any]:
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


class TestSendingDomainsApi:

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
    def test_get_sending_domains_should_raise_api_errors(
        self,
        sending_domains_api: SendingDomainsApi,
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
            sending_domains_api.get_list()

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_sending_domains_should_return_domains_list(
        self, sending_domains_api: SendingDomainsApi, sample_sending_domain_dict: dict
    ) -> None:
        responses.get(
            BASE_SENDING_DOMAINS_URL,
            json={"data": [sample_sending_domain_dict]},
            status=200,
        )

        domains = sending_domains_api.get_list()

        assert isinstance(domains, list)
        assert all(isinstance(d, SendingDomain) for d in domains)
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
    def test_get_sending_domain_by_id_should_raise_api_errors(
        self,
        sending_domains_api: SendingDomainsApi,
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
            sending_domains_api.get_by_id(DOMAIN_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_sending_domain_by_id_should_return_sending_domain(
        self, sending_domains_api: SendingDomainsApi, sample_sending_domain_dict: dict
    ) -> None:
        responses.get(
            f"{BASE_SENDING_DOMAINS_URL}/{DOMAIN_ID}",
            json=sample_sending_domain_dict,
            status=200,
        )

        domain = sending_domains_api.get_by_id(DOMAIN_ID)

        assert isinstance(domain, SendingDomain)
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
    def test_create_sending_domain_should_raise_api_errors(
        self,
        sending_domains_api: SendingDomainsApi,
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
            params = CreateSendingDomainParams(domain_name="example.com")
            sending_domains_api.create(params)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_create_sending_domain_should_return_created_domain(
        self, sending_domains_api: SendingDomainsApi, sample_sending_domain_dict: dict
    ) -> None:
        responses.post(
            BASE_SENDING_DOMAINS_URL,
            json=sample_sending_domain_dict,
            status=200,
        )

        params = CreateSendingDomainParams(domain_name="example.com")
        domain = sending_domains_api.create(params)

        assert isinstance(domain, SendingDomain)
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
                conftest.INTERNAL_SERVER_ERROR_STATUS_CODE,
                conftest.INTERNAL_SERVER_ERROR_RESPONSE,
                conftest.INTERNAL_SERVER_ERROR_MESSAGE,
            ),
        ],
    )
    @responses.activate
    def test_delete_sending_domain_should_raise_api_errors(
        self,
        sending_domains_api: SendingDomainsApi,
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
            sending_domains_api.delete(DOMAIN_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_delete_sending_domain_should_return_deleted_object(
        self, sending_domains_api: SendingDomainsApi
    ) -> None:
        responses.delete(
            f"{BASE_SENDING_DOMAINS_URL}/{DOMAIN_ID}",
            status=204,
        )

        deleted_domain = sending_domains_api.delete(DOMAIN_ID)

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
        sending_domains_api: SendingDomainsApi,
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
            sending_domains_api.send_setup_instructions(DOMAIN_ID, params)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_send_setup_instructions_should_return_success_response(
        self, sending_domains_api: SendingDomainsApi
    ) -> None:
        responses.post(
            f"{BASE_SENDING_DOMAINS_URL}/{DOMAIN_ID}/send_setup_instructions",
            status=204,
        )

        params = SendSetupInstructionsParams(email="admin@example.com")
        response = sending_domains_api.send_setup_instructions(DOMAIN_ID, params)

        assert isinstance(response, SendSetupInstructionsResponse)
        assert response.message == "Instructions email has been sent successfully"
