from typing import Any
from urllib.parse import parse_qs
from urllib.parse import urlparse

import pytest
import responses

from mailtrap.api.resources.email_campaigns import EmailCampaignsApi
from mailtrap.config import GENERAL_HOST
from mailtrap.exceptions import APIError
from mailtrap.http import HttpClient
from mailtrap.models.email_campaigns import CampaignTemplate
from mailtrap.models.email_campaigns import CreateEmailCampaignParams
from mailtrap.models.email_campaigns import DeliveryOptions
from mailtrap.models.email_campaigns import EmailCampaign
from mailtrap.models.email_campaigns import EmailCampaignListResponse
from mailtrap.models.email_campaigns import EmailCampaignStats
from mailtrap.models.email_campaigns import ReplyTo
from mailtrap.models.email_campaigns import UpdateEmailCampaignParams
from tests import conftest

ACCOUNT_ID = "26730"
CAMPAIGN_ID = 4567
# The endpoint is token-scoped, NOT under /api/accounts/{account_id}.
BASE_CAMPAIGNS_URL = f"https://{GENERAL_HOST}/api/email_campaigns"


@pytest.fixture
def client() -> EmailCampaignsApi:
    return EmailCampaignsApi(client=HttpClient(GENERAL_HOST), account_id=ACCOUNT_ID)


@pytest.fixture
def sample_stats_dict() -> dict[str, Any]:
    return {
        "delivery_count": 1450,
        "open_count": 820,
        "click_count": 310,
        "bounce_count": 30,
        "unsubscription_count": 12,
        "sent_count": 1500,
        "spam_count": 5,
        "message_count": 1500,
        "reject_count": 20,
        "delivery_rate": 0.9667,
        "open_rate": 0.5655,
        "click_rate": 0.2138,
        "bounce_rate": 0.02,
        "spam_rate": 0.0033,
        "unsubscription_rate": 0.0083,
    }


@pytest.fixture
def sample_campaign_dict() -> dict[str, Any]:
    return {
        "id": CAMPAIGN_ID,
        "type": "EmailCampaign",
        "mailsend_domain_id": 123,
        "mailsend_domain_name": "acme.com",
        "name": "Spring Sale",
        "from_local_part": "news",
        "from_display_name": "Acme Marketing",
        "reply_to": {
            "display_name": "Acme Support",
            "local_part": "support",
            "domain": "acme.com",
        },
        "current_state": "draft",
        "current_state_metadata": {"reason": None, "errors": []},
        "created_at": "2026-05-01T10:15:00.000Z",
        "updated_at": "2026-05-02T09:00:00.000Z",
        "last_started_at": None,
        "last_started_at_date": None,
        "recipient_total_count": 1500,
        "delivery_mode": "immediate",
        "delivery_options": {"emails_per_hour": 1000},
        "scheduled_for": None,
        "audience_defined": True,
        "template": {"id": 789, "subject": "Spring is here — 30% off"},
    }


class TestEmailCampaignsApi:

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
    def test_get_list_should_raise_api_errors(
        self,
        client: EmailCampaignsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.get(BASE_CAMPAIGNS_URL, status=status_code, json=response_json)

        with pytest.raises(APIError) as exc_info:
            client.get_list()

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_list_should_return_campaigns_and_pagination(
        self, client: EmailCampaignsApi, sample_campaign_dict: dict
    ) -> None:
        # List items omit `audience_defined`.
        list_item = {k: v for k, v in sample_campaign_dict.items()}
        del list_item["audience_defined"]
        responses.get(
            BASE_CAMPAIGNS_URL,
            json={
                "data": [
                    list_item,
                    {"id": 4568, "name": "Summer Sale", "current_state": "sent"},
                ],
                "pagination": {
                    "token": 1,
                    "prev_token": None,
                    "next_token": 2,
                    "first_url": f"{BASE_CAMPAIGNS_URL}?per_page=50&token=1",
                    "prev_url": None,
                    "current_url": f"{BASE_CAMPAIGNS_URL}?per_page=50&token=1",
                    "next_url": f"{BASE_CAMPAIGNS_URL}?per_page=50&token=2",
                },
            },
            status=200,
        )

        result = client.get_list()

        assert isinstance(result, EmailCampaignListResponse)
        assert all(isinstance(c, EmailCampaign) for c in result.data)
        assert len(result.data) == 2
        assert result.data[0].id == CAMPAIGN_ID
        assert result.data[0].name == "Spring Sale"
        # audience_defined is omitted from list items -> Optional, defaults None.
        assert result.data[0].audience_defined is None
        assert result.pagination is not None
        assert result.pagination.token == 1
        assert result.pagination.prev_token is None
        assert result.pagination.next_token == 2

    @responses.activate
    def test_get_list_should_return_empty_list(self, client: EmailCampaignsApi) -> None:
        responses.get(
            BASE_CAMPAIGNS_URL,
            json={"data": [], "pagination": {"token": 1}},
            status=200,
        )

        result = client.get_list()

        assert isinstance(result, EmailCampaignListResponse)
        assert result.data == []

    @responses.activate
    def test_get_list_should_send_search_per_page_and_token_query_params(
        self, client: EmailCampaignsApi
    ) -> None:
        responses.get(BASE_CAMPAIGNS_URL, json={"data": [], "pagination": {}}, status=200)

        client.get_list(per_page=25, search="Spring", token=2)

        query = parse_qs(urlparse(responses.calls[0].request.url).query)
        # The name filter must serialize to `search`, not `name`.
        assert query["search"] == ["Spring"]
        assert query["per_page"] == ["25"]
        assert query["token"] == ["2"]
        assert "name" not in query

    @pytest.mark.parametrize(
        "status_code,response_json,expected_error_message",
        [
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
        ],
    )
    @responses.activate
    def test_get_by_id_should_raise_api_errors(
        self,
        client: EmailCampaignsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.get(
            f"{BASE_CAMPAIGNS_URL}/{CAMPAIGN_ID}",
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.get_by_id(CAMPAIGN_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_by_id_should_return_bare_campaign(
        self,
        client: EmailCampaignsApi,
        sample_campaign_dict: dict,
        sample_stats_dict: dict,
    ) -> None:
        # get returns a bare EmailCampaign (no `data` envelope), and may carry stats.
        responses.get(
            f"{BASE_CAMPAIGNS_URL}/{CAMPAIGN_ID}",
            json={**sample_campaign_dict, "stats": sample_stats_dict},
            status=200,
        )

        campaign = client.get_by_id(CAMPAIGN_ID)

        assert isinstance(campaign, EmailCampaign)
        assert campaign.id == CAMPAIGN_ID
        assert campaign.current_state == "draft"
        assert campaign.audience_defined is True
        assert campaign.reply_to is not None
        assert campaign.reply_to.local_part == "support"
        assert campaign.template is not None
        assert campaign.template.id == 789
        assert campaign.delivery_options is not None
        assert campaign.delivery_options.emails_per_hour == 1000
        assert isinstance(campaign.stats, EmailCampaignStats)
        assert campaign.stats.delivery_count == 1450
        assert campaign.stats.open_rate == 0.5655

    @pytest.mark.parametrize(
        "status_code,response_json,expected_error_message",
        [
            (
                conftest.UNAUTHORIZED_STATUS_CODE,
                conftest.UNAUTHORIZED_RESPONSE,
                conftest.UNAUTHORIZED_ERROR_MESSAGE,
            ),
            (
                conftest.VALIDATION_ERRORS_STATUS_CODE,
                {"errors": {"mailsend_domain_id": ["can't be blank"]}},
                "mailsend_domain_id: can't be blank",
            ),
        ],
    )
    @responses.activate
    def test_create_should_raise_api_errors(
        self,
        client: EmailCampaignsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.post(BASE_CAMPAIGNS_URL, status=status_code, json=response_json)

        with pytest.raises(APIError) as exc_info:
            client.create(
                CreateEmailCampaignParams(name="Spring Sale", mailsend_domain_id=123)
            )

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_create_should_wrap_body_and_return_bare_campaign(
        self, client: EmailCampaignsApi, sample_campaign_dict: dict
    ) -> None:
        responses.post(BASE_CAMPAIGNS_URL, json=sample_campaign_dict, status=200)

        campaign = client.create(
            CreateEmailCampaignParams(
                name="Spring Sale",
                mailsend_domain_id=123,
                from_display_name="Acme Marketing",
                from_local_part="news",
                reply_to=ReplyTo(
                    display_name="Acme Support",
                    local_part="support",
                    domain="acme.com",
                ),
                template_attributes=CampaignTemplate(subject="Spring is here — 30% off"),
            )
        )

        assert isinstance(campaign, EmailCampaign)
        assert campaign.id == CAMPAIGN_ID
        assert campaign.current_state == "draft"

        assert len(responses.calls) == 1
        assert responses.calls[0].request.body == (
            b'{"email_campaign": {"name": "Spring Sale", '
            b'"mailsend_domain_id": 123, "from_display_name": "Acme Marketing", '
            b'"from_local_part": "news", "reply_to": {"display_name": '
            b'"Acme Support", "local_part": "support", "domain": "acme.com"}, '
            b'"template_attributes": {"subject": '
            b'"Spring is here \\u2014 30% off"}}}'
        )

    @responses.activate
    def test_update_should_send_only_supplied_fields_wrapped(
        self, client: EmailCampaignsApi, sample_campaign_dict: dict
    ) -> None:
        responses.patch(
            f"{BASE_CAMPAIGNS_URL}/{CAMPAIGN_ID}",
            json={
                **sample_campaign_dict,
                "delivery_mode": "scheduled",
                "scheduled_for": "2026-06-01T09:00:00.000Z",
            },
            status=200,
        )

        campaign = client.update(
            CAMPAIGN_ID,
            UpdateEmailCampaignParams(
                delivery_mode="scheduled",
                scheduled_for="2026-06-01T09:00:00.000Z",
                delivery_options=DeliveryOptions(emails_per_hour=1000),
                template_attributes=CampaignTemplate(id=789, subject="New subject"),
            ),
        )

        assert isinstance(campaign, EmailCampaign)
        assert campaign.delivery_mode == "scheduled"
        assert campaign.scheduled_for == "2026-06-01T09:00:00.000Z"

        assert responses.calls[0].request.body == (
            b'{"email_campaign": {"delivery_mode": "scheduled", '
            b'"scheduled_for": "2026-06-01T09:00:00.000Z", '
            b'"delivery_options": {"emails_per_hour": 1000}, '
            b'"template_attributes": {"id": 789, "subject": "New subject"}}}'
        )

    @pytest.mark.parametrize(
        "status_code,response_json,expected_error_message",
        [
            (
                conftest.NOT_FOUND_STATUS_CODE,
                conftest.NOT_FOUND_RESPONSE,
                conftest.NOT_FOUND_ERROR_MESSAGE,
            ),
            (
                conftest.VALIDATION_ERRORS_STATUS_CODE,
                {"errors": {"base": ["campaign is sending"]}},
                "base: campaign is sending",
            ),
        ],
    )
    @responses.activate
    def test_update_should_raise_api_errors(
        self,
        client: EmailCampaignsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.patch(
            f"{BASE_CAMPAIGNS_URL}/{CAMPAIGN_ID}",
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.update(CAMPAIGN_ID, UpdateEmailCampaignParams(name="x"))

        assert expected_error_message in str(exc_info.value)

    @pytest.mark.parametrize(
        "status_code,response_json,expected_error_message",
        [
            (
                conftest.NOT_FOUND_STATUS_CODE,
                conftest.NOT_FOUND_RESPONSE,
                conftest.NOT_FOUND_ERROR_MESSAGE,
            ),
            (
                conftest.VALIDATION_ERRORS_STATUS_CODE,
                {"errors": {"base": ["campaign is sending"]}},
                "base: campaign is sending",
            ),
        ],
    )
    @responses.activate
    def test_delete_should_raise_api_errors(
        self,
        client: EmailCampaignsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.delete(
            f"{BASE_CAMPAIGNS_URL}/{CAMPAIGN_ID}",
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.delete(CAMPAIGN_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_delete_should_return_deleted_campaign(
        self, client: EmailCampaignsApi, sample_campaign_dict: dict
    ) -> None:
        # delete returns HTTP 200 + the deleted entity (bare EmailCampaign), not 204.
        responses.delete(
            f"{BASE_CAMPAIGNS_URL}/{CAMPAIGN_ID}",
            json=sample_campaign_dict,
            status=200,
        )

        result = client.delete(CAMPAIGN_ID)

        assert isinstance(result, EmailCampaign)
        assert result.id == CAMPAIGN_ID
        assert result.name == "Spring Sale"

    @pytest.mark.parametrize(
        "status_code,response_json,expected_error_message",
        [
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
        ],
    )
    @responses.activate
    def test_get_stats_should_raise_api_errors(
        self,
        client: EmailCampaignsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.get(
            f"{BASE_CAMPAIGNS_URL}/{CAMPAIGN_ID}/stats",
            status=status_code,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.get_stats(CAMPAIGN_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_stats_should_return_bare_stats(
        self, client: EmailCampaignsApi, sample_stats_dict: dict
    ) -> None:
        # stats returns a bare EmailCampaignStats (no `data` envelope).
        responses.get(
            f"{BASE_CAMPAIGNS_URL}/{CAMPAIGN_ID}/stats",
            json=sample_stats_dict,
            status=200,
        )

        stats = client.get_stats(CAMPAIGN_ID)

        assert isinstance(stats, EmailCampaignStats)
        assert stats.delivery_count == 1450
        assert stats.open_count == 820
        assert stats.unsubscription_rate == 0.0083

    @responses.activate
    def test_get_stats_should_return_zeros_when_not_started(
        self, client: EmailCampaignsApi
    ) -> None:
        zeros = {
            "delivery_count": 0,
            "open_count": 0,
            "click_count": 0,
            "bounce_count": 0,
            "unsubscription_count": 0,
            "sent_count": 0,
            "spam_count": 0,
            "message_count": 0,
            "reject_count": 0,
            "delivery_rate": 0.0,
            "open_rate": 0.0,
            "click_rate": 0.0,
            "bounce_rate": 0.0,
            "spam_rate": 0.0,
            "unsubscription_rate": 0.0,
        }
        responses.get(f"{BASE_CAMPAIGNS_URL}/{CAMPAIGN_ID}/stats", json=zeros, status=200)

        stats = client.get_stats(CAMPAIGN_ID)

        assert isinstance(stats, EmailCampaignStats)
        assert stats.delivery_count == 0
        assert stats.delivery_rate == 0.0
