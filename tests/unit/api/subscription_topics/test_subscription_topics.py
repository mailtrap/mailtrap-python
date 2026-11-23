from typing import Any
from typing import Optional
from urllib.parse import parse_qs
from urllib.parse import urlparse

import pytest
import responses

from mailtrap.api.resources.subscription_topics import SubscriptionTopicsApi
from mailtrap.config import GENERAL_HOST
from mailtrap.exceptions import APIError
from mailtrap.http import HttpClient
from mailtrap.models.subscription_topics import SubscriptionTopic
from mailtrap.models.subscription_topics import SubscriptionTopicListParams
from mailtrap.models.subscription_topics import SubscriptionTopicListResponse
from tests import conftest

TOPIC_ID = 17
DOMAIN_ID = 4321
BASE_TOPICS_URL = f"https://{GENERAL_HOST}/api/subscription_topics"


@pytest.fixture
def client() -> SubscriptionTopicsApi:
    return SubscriptionTopicsApi(client=HttpClient(GENERAL_HOST))


@pytest.fixture
def sample_topic_dict() -> dict[str, Any]:
    return {
        "id": TOPIC_ID,
        "name": "Weekly digest",
        "description": "A summary of the week, every Monday",
        "domain_id": DOMAIN_ID,
        "deleted_at": None,
        "created_at": "2026-05-01T10:15:00.000Z",
        "updated_at": "2026-05-02T09:00:00.000Z",
    }


class TestSubscriptionTopicsApi:

    @pytest.mark.parametrize(
        "status_code,response_json,expected_error_message",
        [
            (
                conftest.UNAUTHORIZED_STATUS_CODE,
                conftest.UNAUTHORIZED_RESPONSE,
                conftest.UNAUTHORIZED_ERROR_MESSAGE,
            ),
            (
                conftest.RATE_LIMIT_ERROR_STATUS_CODE,
                conftest.RATE_LIMIT_ERROR_RESPONSE,
                conftest.RATE_LIMIT_ERROR_MESSAGE,
            ),
            (
                conftest.VALIDATION_ERRORS_STATUS_CODE,
                {"errors": "token is out of range"},
                "token is out of range",
            ),
        ],
    )
    @responses.activate
    def test_get_list_should_raise_api_errors(
        self,
        client: SubscriptionTopicsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.get(BASE_TOPICS_URL, status=status_code, json=response_json)

        with pytest.raises(APIError) as exc_info:
            client.get_list()

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_get_list_should_raise_forbidden_without_topics(
        self, client: SubscriptionTopicsApi
    ) -> None:
        # An account without subscription topics gets a 403 with an empty body.
        responses.get(BASE_TOPICS_URL, status=conftest.FORBIDDEN_STATUS_CODE, body="")

        with pytest.raises(APIError) as exc_info:
            client.get_list()

        assert exc_info.value.status == conftest.FORBIDDEN_STATUS_CODE

    @responses.activate
    def test_get_list_should_return_topics_and_pagination(
        self, client: SubscriptionTopicsApi, sample_topic_dict: dict
    ) -> None:
        all_domains_topic = {
            **sample_topic_dict,
            "id": 18,
            "name": "Product news",
            "description": None,
            "domain_id": None,
        }
        responses.get(
            BASE_TOPICS_URL,
            json={
                "data": [sample_topic_dict, all_domains_topic],
                "pagination": {
                    "token": 1,
                    "prev_token": None,
                    "next_token": 2,
                    "first_url": f"{BASE_TOPICS_URL}?per_page=2&token=1",
                    "prev_url": None,
                    "current_url": f"{BASE_TOPICS_URL}?per_page=2&token=1",
                    "next_url": f"{BASE_TOPICS_URL}?per_page=2&token=2",
                },
            },
            status=200,
        )

        result = client.get_list()

        assert isinstance(result, SubscriptionTopicListResponse)
        assert all(isinstance(t, SubscriptionTopic) for t in result.data)
        assert result.data[0] == SubscriptionTopic(**sample_topic_dict)
        assert result.data[1].description is None
        assert result.data[1].domain_id is None
        assert result.pagination is not None
        assert result.pagination.token == 1
        assert result.pagination.next_token == 2

    @responses.activate
    def test_get_list_should_return_empty_list(
        self, client: SubscriptionTopicsApi
    ) -> None:
        responses.get(
            BASE_TOPICS_URL, json={"data": [], "pagination": {"token": 1}}, status=200
        )

        result = client.get_list()

        assert result.data == []

    @responses.activate
    def test_get_list_should_send_per_page_and_token_query_params(
        self, client: SubscriptionTopicsApi
    ) -> None:
        responses.get(BASE_TOPICS_URL, json={"data": [], "pagination": {}}, status=200)

        client.get_list(SubscriptionTopicListParams(per_page=25, token=2))

        query = parse_qs(urlparse(responses.calls[0].request.url).query)
        assert query == {"per_page": ["25"], "token": ["2"]}

    @responses.activate
    def test_get_list_should_send_no_query_params_by_default(
        self, client: SubscriptionTopicsApi
    ) -> None:
        responses.get(BASE_TOPICS_URL, json={"data": [], "pagination": {}}, status=200)

        client.get_list()

        assert urlparse(responses.calls[0].request.url).query == ""

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
        client: SubscriptionTopicsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.get(
            f"{BASE_TOPICS_URL}/{TOPIC_ID}", status=status_code, json=response_json
        )

        with pytest.raises(APIError) as exc_info:
            client.get_by_id(TOPIC_ID)

        assert expected_error_message in str(exc_info.value)

    # A deleted topic is returned too, with deleted_at set.
    @pytest.mark.parametrize("deleted_at", [None, "2026-05-03T12:00:00.000Z"])
    @responses.activate
    def test_get_by_id_should_unwrap_data_envelope(
        self,
        client: SubscriptionTopicsApi,
        sample_topic_dict: dict,
        deleted_at: Optional[str],
    ) -> None:
        data = {**sample_topic_dict, "deleted_at": deleted_at}
        responses.get(f"{BASE_TOPICS_URL}/{TOPIC_ID}", json={"data": data}, status=200)

        topic = client.get_by_id(TOPIC_ID)

        assert topic == SubscriptionTopic(**data)
