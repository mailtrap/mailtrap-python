import json
from typing import Any
from urllib.parse import parse_qs
from urllib.parse import urlparse

import pytest
import responses

from mailtrap.api.resources.email_campaigns import EmailCampaignsApi
from mailtrap.config import GENERAL_HOST
from mailtrap.exceptions import APIError
from mailtrap.http import HttpClient
from mailtrap.models.common import DeletedObject
from mailtrap.models.email_campaigns import CreateEmailCampaignParams
from mailtrap.models.email_campaigns import CreateEmailCampaignTemplateAttributes
from mailtrap.models.email_campaigns import EmailCampaign
from mailtrap.models.email_campaigns import EmailCampaignDeliveryOptions
from mailtrap.models.email_campaigns import EmailCampaignListParams
from mailtrap.models.email_campaigns import EmailCampaignListResponse
from mailtrap.models.email_campaigns import EmailCampaignReplyTo
from mailtrap.models.email_campaigns import EmailCampaignStats
from mailtrap.models.email_campaigns import EmailCampaignStatsParams
from mailtrap.models.email_campaigns import EmailCampaignTemplateAttributes
from mailtrap.models.email_campaigns import ScheduleEmailCampaignParams
from mailtrap.models.email_campaigns import UpdateEmailCampaignParams
from tests import conftest

CAMPAIGN_ID = 4567
DOMAIN_ID = 4321
TOPIC_ID = 17
BASE_CAMPAIGNS_URL = f"https://{GENERAL_HOST}/api/email_campaigns"


@pytest.fixture
def client() -> EmailCampaignsApi:
    return EmailCampaignsApi(client=HttpClient(GENERAL_HOST))


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
        "domain_id": DOMAIN_ID,
        "domain_name": "acme.com",
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
        "contact_list_ids": [55, 56],
        "contact_segment_ids": [12],
        "delivery_mode": "rapid",
        "delivery_options": {"emails_per_hour": 1000},
        "subscription_topic_id": None,
        "template": {
            "id": 789,
            "subject": "Spring is here — 30% off",
            "merge_tags": ["first_name"],
            "body_html": "<html><body><h1>Hi {{first_name}}!</h1></body></html>",
            "body_text": None,
        },
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
        # List items omit template bodies.
        list_item = {
            **sample_campaign_dict,
            "template": {
                "id": 789,
                "subject": "Spring is here — 30% off",
                "merge_tags": ["first_name"],
            },
        }
        responses.get(
            BASE_CAMPAIGNS_URL,
            json={
                "data": [
                    list_item,
                    {"id": 4568, "name": "Summer Sale", "current_state": "finished"},
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
        assert result.data[0].contact_list_ids == [55, 56]
        assert result.data[0].template is not None
        assert result.data[0].template.body_html is None
        assert result.data[1].current_state == "finished"
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

        client.get_list(EmailCampaignListParams(per_page=25, search="Spring", token=2))

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
    def test_get_by_id_should_unwrap_data_envelope(
        self, client: EmailCampaignsApi, sample_campaign_dict: dict
    ) -> None:
        responses.get(
            f"{BASE_CAMPAIGNS_URL}/{CAMPAIGN_ID}",
            json={"data": sample_campaign_dict},
            status=200,
        )

        campaign = client.get_by_id(CAMPAIGN_ID)

        assert isinstance(campaign, EmailCampaign)
        assert campaign.id == CAMPAIGN_ID
        assert campaign.domain_id == DOMAIN_ID
        assert campaign.domain_name == "acme.com"
        assert campaign.current_state == "draft"
        assert campaign.contact_list_ids == [55, 56]
        assert campaign.contact_segment_ids == [12]
        assert campaign.delivery_mode == "rapid"
        assert campaign.reply_to is not None
        assert campaign.reply_to.local_part == "support"
        assert campaign.template is not None
        assert campaign.template.id == 789
        assert campaign.template.merge_tags == ["first_name"]
        assert campaign.template.body_html is not None
        assert campaign.delivery_options is not None
        assert campaign.delivery_options.emails_per_hour == 1000
        assert campaign.subscription_topic_id is None

    @responses.activate
    def test_get_by_id_should_parse_subscription_topic_id(
        self, client: EmailCampaignsApi, sample_campaign_dict: dict
    ) -> None:
        responses.get(
            f"{BASE_CAMPAIGNS_URL}/{CAMPAIGN_ID}",
            json={"data": {**sample_campaign_dict, "subscription_topic_id": TOPIC_ID}},
            status=200,
        )

        campaign = client.get_by_id(CAMPAIGN_ID)

        assert campaign.subscription_topic_id == TOPIC_ID

    @responses.activate
    def test_get_by_id_should_parse_state_metadata_errors(
        self, client: EmailCampaignsApi, sample_campaign_dict: dict
    ) -> None:
        failed = {
            **sample_campaign_dict,
            "current_state": "failed",
            "current_state_metadata": {
                "error": "Sending failed",
                "errors": [{"message": "Invalid recipient address", "rcpt_index": 0}],
            },
        }
        responses.get(
            f"{BASE_CAMPAIGNS_URL}/{CAMPAIGN_ID}",
            json={"data": failed},
            status=200,
        )

        campaign = client.get_by_id(CAMPAIGN_ID)

        assert campaign.current_state_metadata is not None
        assert campaign.current_state_metadata.error == "Sending failed"
        assert len(campaign.current_state_metadata.errors) == 1
        assert (
            campaign.current_state_metadata.errors[0].message
            == "Invalid recipient address"
        )
        assert campaign.current_state_metadata.errors[0].rcpt_index == 0

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
                {"errors": {"domain_id": ["must exist"]}},
                "domain_id: must exist",
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
                CreateEmailCampaignParams(
                    name="Spring Sale",
                    domain_id=DOMAIN_ID,
                    from_local_part="news",
                    template_attributes=CreateEmailCampaignTemplateAttributes(
                        subject="Spring!"
                    ),
                )
            )

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_create_should_send_flat_body_and_unwrap_data_envelope(
        self, client: EmailCampaignsApi, sample_campaign_dict: dict
    ) -> None:
        responses.post(
            BASE_CAMPAIGNS_URL, json={"data": sample_campaign_dict}, status=201
        )

        campaign = client.create(
            CreateEmailCampaignParams(
                name="Spring Sale",
                domain_id=DOMAIN_ID,
                from_local_part="news",
                template_attributes=CreateEmailCampaignTemplateAttributes(
                    subject="Spring is here — 30% off"
                ),
                from_display_name="Acme Marketing",
                reply_to=EmailCampaignReplyTo(
                    display_name="Acme Support",
                    local_part="support",
                    domain="acme.com",
                ),
                contact_list_ids=[55, 56],
            )
        )

        assert isinstance(campaign, EmailCampaign)
        assert campaign.id == CAMPAIGN_ID
        assert campaign.current_state == "draft"

        assert len(responses.calls) == 1
        # The request body is flat — no `email_campaign` wrapper.
        assert json.loads(responses.calls[0].request.body) == {
            "name": "Spring Sale",
            "domain_id": 4321,
            "from_local_part": "news",
            "template_attributes": {"subject": "Spring is here — 30% off"},
            "from_display_name": "Acme Marketing",
            "reply_to": {
                "display_name": "Acme Support",
                "local_part": "support",
                "domain": "acme.com",
            },
            "contact_list_ids": [55, 56],
        }

    @responses.activate
    def test_create_should_send_subscription_topic_id(
        self, client: EmailCampaignsApi, sample_campaign_dict: dict
    ) -> None:
        responses.post(
            BASE_CAMPAIGNS_URL,
            json={"data": {**sample_campaign_dict, "subscription_topic_id": TOPIC_ID}},
            status=201,
        )

        campaign = client.create(
            CreateEmailCampaignParams(
                name="Spring Sale",
                domain_id=DOMAIN_ID,
                from_local_part="news",
                template_attributes=CreateEmailCampaignTemplateAttributes(
                    subject="Spring!"
                ),
                subscription_topic_id=TOPIC_ID,
            )
        )

        assert campaign.subscription_topic_id == TOPIC_ID
        assert json.loads(responses.calls[0].request.body) == {
            "name": "Spring Sale",
            "domain_id": DOMAIN_ID,
            "from_local_part": "news",
            "template_attributes": {"subject": "Spring!"},
            "subscription_topic_id": TOPIC_ID,
        }

    @responses.activate
    def test_update_should_send_subscription_topic_id(
        self, client: EmailCampaignsApi, sample_campaign_dict: dict
    ) -> None:
        responses.patch(
            f"{BASE_CAMPAIGNS_URL}/{CAMPAIGN_ID}",
            json={"data": {**sample_campaign_dict, "subscription_topic_id": TOPIC_ID}},
            status=200,
        )

        campaign = client.update(
            CAMPAIGN_ID, UpdateEmailCampaignParams(subscription_topic_id=TOPIC_ID)
        )

        assert campaign.subscription_topic_id == TOPIC_ID
        assert json.loads(responses.calls[0].request.body) == {
            "subscription_topic_id": TOPIC_ID
        }

    @responses.activate
    def test_update_should_send_only_supplied_fields_flat(
        self, client: EmailCampaignsApi, sample_campaign_dict: dict
    ) -> None:
        responses.patch(
            f"{BASE_CAMPAIGNS_URL}/{CAMPAIGN_ID}",
            json={"data": {**sample_campaign_dict, "delivery_mode": "gradual"}},
            status=200,
        )

        campaign = client.update(
            CAMPAIGN_ID,
            UpdateEmailCampaignParams(
                template_attributes=EmailCampaignTemplateAttributes(
                    subject="New subject",
                    body_html="<html><body>Hi</body></html>",
                    merge_tags=["first_name"],
                ),
                delivery_mode="gradual",
                delivery_options=EmailCampaignDeliveryOptions(emails_per_hour=1000),
                contact_segment_ids=[12],
            ),
        )

        assert isinstance(campaign, EmailCampaign)
        assert campaign.delivery_mode == "gradual"

        assert json.loads(responses.calls[0].request.body) == {
            "template_attributes": {
                "subject": "New subject",
                "body_html": "<html><body>Hi</body></html>",
                "merge_tags": ["first_name"],
            },
            "delivery_mode": "gradual",
            "delivery_options": {"emails_per_hour": 1000},
            "contact_segment_ids": [12],
        }

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
                {"errors": {"base": ["Campaign is not editable"]}},
                "base: Campaign is not editable",
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
    def test_delete_should_return_deleted_object_on_204(
        self, client: EmailCampaignsApi
    ) -> None:
        responses.delete(f"{BASE_CAMPAIGNS_URL}/{CAMPAIGN_ID}", status=204)

        result = client.delete(CAMPAIGN_ID)

        assert isinstance(result, DeletedObject)
        assert result.id == CAMPAIGN_ID

    @pytest.mark.parametrize("action", ["start", "cancel", "terminate", "reset"])
    @responses.activate
    def test_lifecycle_actions_should_post_and_unwrap_data_envelope(
        self, client: EmailCampaignsApi, sample_campaign_dict: dict, action: str
    ) -> None:
        responses.post(
            f"{BASE_CAMPAIGNS_URL}/{CAMPAIGN_ID}/{action}",
            json={"data": {**sample_campaign_dict, "current_state": "started"}},
            status=200,
        )

        campaign = getattr(client, action)(CAMPAIGN_ID)

        assert isinstance(campaign, EmailCampaign)
        assert campaign.id == CAMPAIGN_ID
        assert campaign.current_state == "started"
        assert responses.calls[0].request.body is None

    @pytest.mark.parametrize(
        "response_json,expected_error_message",
        [
            (
                {"errors": "Cannot transition from 'started' to 'scheduled'"},
                "Cannot transition from 'started' to 'scheduled'",
            ),
            (
                {"errors": ["Campaign design can't be blank"]},
                "Campaign design can't be blank",
            ),
        ],
    )
    @responses.activate
    def test_start_should_raise_action_validation_errors(
        self,
        client: EmailCampaignsApi,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.post(
            f"{BASE_CAMPAIGNS_URL}/{CAMPAIGN_ID}/start",
            status=conftest.VALIDATION_ERRORS_STATUS_CODE,
            json=response_json,
        )

        with pytest.raises(APIError) as exc_info:
            client.start(CAMPAIGN_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_schedule_should_send_datetime_and_unwrap_data_envelope(
        self, client: EmailCampaignsApi, sample_campaign_dict: dict
    ) -> None:
        scheduled = {
            **sample_campaign_dict,
            "current_state": "scheduled",
            "current_state_metadata": {"scheduled_at": "2026-06-01T09:00:00.000Z"},
        }
        responses.post(
            f"{BASE_CAMPAIGNS_URL}/{CAMPAIGN_ID}/schedule",
            json={"data": scheduled},
            status=200,
        )

        campaign = client.schedule(
            CAMPAIGN_ID,
            ScheduleEmailCampaignParams(datetime="2026-06-01T09:00:00.000Z"),
        )

        assert isinstance(campaign, EmailCampaign)
        assert campaign.current_state == "scheduled"
        assert campaign.current_state_metadata is not None
        assert campaign.current_state_metadata.scheduled_at == "2026-06-01T09:00:00.000Z"
        assert json.loads(responses.calls[0].request.body) == {
            "datetime": "2026-06-01T09:00:00.000Z"
        }

    @responses.activate
    def test_schedule_should_raise_api_error_for_invalid_datetime(
        self, client: EmailCampaignsApi
    ) -> None:
        responses.post(
            f"{BASE_CAMPAIGNS_URL}/{CAMPAIGN_ID}/schedule",
            status=conftest.VALIDATION_ERRORS_STATUS_CODE,
            json={"errors": "Datetime must be in the future"},
        )

        with pytest.raises(APIError) as exc_info:
            client.schedule(
                CAMPAIGN_ID,
                ScheduleEmailCampaignParams(datetime="2020-01-01T00:00:00.000Z"),
            )

        assert "Datetime must be in the future" in str(exc_info.value)

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
    def test_get_stats_should_unwrap_data_envelope(
        self, client: EmailCampaignsApi, sample_stats_dict: dict
    ) -> None:
        responses.get(
            f"{BASE_CAMPAIGNS_URL}/{CAMPAIGN_ID}/stats",
            json={"data": sample_stats_dict},
            status=200,
        )

        stats = client.get_stats(CAMPAIGN_ID)

        assert isinstance(stats, EmailCampaignStats)
        assert stats.delivery_count == 1450
        assert stats.open_count == 820
        assert stats.unsubscription_rate == 0.0083

    @responses.activate
    def test_get_stats_should_send_date_query_params(
        self, client: EmailCampaignsApi, sample_stats_dict: dict
    ) -> None:
        responses.get(
            f"{BASE_CAMPAIGNS_URL}/{CAMPAIGN_ID}/stats",
            json={"data": sample_stats_dict},
            status=200,
        )

        client.get_stats(
            CAMPAIGN_ID,
            EmailCampaignStatsParams(start_date="2026-05-01", end_date="2026-05-31"),
        )

        query = parse_qs(urlparse(responses.calls[0].request.url).query)
        assert query["start_date"] == ["2026-05-01"]
        assert query["end_date"] == ["2026-05-31"]

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
            "delivery_rate": 0.0,
            "open_rate": 0.0,
            "click_rate": 0.0,
            "bounce_rate": 0.0,
            "spam_rate": 0.0,
            "unsubscription_rate": 0.0,
        }
        responses.get(
            f"{BASE_CAMPAIGNS_URL}/{CAMPAIGN_ID}/stats",
            json={"data": zeros},
            status=200,
        )

        stats = client.get_stats(CAMPAIGN_ID)

        assert isinstance(stats, EmailCampaignStats)
        assert stats.delivery_count == 0
        assert stats.delivery_rate == 0.0
