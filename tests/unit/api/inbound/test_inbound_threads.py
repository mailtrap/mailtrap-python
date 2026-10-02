import pytest
import responses

from mailtrap.api.resources.inbound_threads import InboundThreadsApi
from mailtrap.config import GENERAL_HOST
from mailtrap.exceptions import APIError
from mailtrap.http import HttpClient
from mailtrap.models.common import DeletedObject
from mailtrap.models.inbound import InboundForwardOutcome
from mailtrap.models.inbound import InboundThread
from mailtrap.models.inbound import InboundThreadMessageDelivery
from mailtrap.models.inbound import InboundThreadsListResponse
from tests import conftest

INBOX_ID = 9
THREAD_ID = "1871574677878845504"
BASE_URL = f"https://{GENERAL_HOST}/api/inbound/inboxes/{INBOX_ID}/threads"


@pytest.fixture
def threads_api() -> InboundThreadsApi:
    return InboundThreadsApi(client=HttpClient(GENERAL_HOST))


class TestInboundThreadsApi:

    @responses.activate
    def test_get_list_should_return_page(self, threads_api: InboundThreadsApi) -> None:
        responses.get(
            BASE_URL,
            json={
                "data": [
                    {
                        "id": THREAD_ID,
                        "subject": "Billing",
                        "message_count": 2,
                        "size": 100,
                        "first_message_at": "2026-01-15T10:00:00Z",
                        "last_activity_at": "2026-01-15T11:00:00Z",
                    }
                ],
                "total_count": 1,
                "last_id": THREAD_ID,
            },
            status=200,
        )

        page = threads_api.get_list(INBOX_ID)

        assert isinstance(page, InboundThreadsListResponse)
        assert page.total_count == 1
        assert page.data[0].message_count == 2

    @responses.activate
    def test_get_list_should_pass_last_id_cursor(
        self, threads_api: InboundThreadsApi
    ) -> None:
        responses.get(
            BASE_URL, json={"data": [], "total_count": 0, "last_id": None}, status=200
        )

        threads_api.get_list(INBOX_ID, last_id="cursor-1")

        assert "last_id=cursor-1" in responses.calls[-1].request.url

    @responses.activate
    def test_get_list_should_pass_search(self, threads_api: InboundThreadsApi) -> None:
        responses.get(
            BASE_URL, json={"data": [], "total_count": 0, "last_id": None}, status=200
        )

        threads_api.get_list(INBOX_ID, search="acme invoice")

        url = responses.calls[-1].request.url
        assert "search=acme+invoice" in url
        assert "last_id" not in url

    @responses.activate
    def test_get_list_should_combine_search_with_last_id(
        self, threads_api: InboundThreadsApi
    ) -> None:
        responses.get(
            BASE_URL, json={"data": [], "total_count": 0, "last_id": None}, status=200
        )

        threads_api.get_list(INBOX_ID, last_id="cursor-1", search="acme")

        url = responses.calls[-1].request.url
        assert "last_id=cursor-1" in url
        assert "search=acme" in url

    @responses.activate
    def test_get_list_should_raise_on_invalid_search(
        self, threads_api: InboundThreadsApi
    ) -> None:
        responses.get(
            BASE_URL,
            json={"errors": {"search": ["is too long (maximum is 256 characters)"]}},
            status=400,
        )

        with pytest.raises(APIError) as exc_info:
            threads_api.get_list(INBOX_ID, search="a" * 257)

        assert "search" in str(exc_info.value)

    @responses.activate
    def test_get_by_id_should_return_thread_with_messages(
        self, threads_api: InboundThreadsApi
    ) -> None:
        responses.get(
            f"{BASE_URL}/{THREAD_ID}",
            json={
                "id": THREAD_ID,
                "subject": "Billing",
                "message_count": 1,
                "size": 50,
                "first_message_at": "2026-01-15T10:00:00Z",
                "last_activity_at": "2026-01-15T10:00:00Z",
                "messages": [
                    {
                        "visibility_status": "available",
                        "direction": "inbound",
                        "from": "customer@example.com",
                        "forwards": [
                            {
                                "rule_id": 7,
                                "rule_name": "Copy to support team",
                                "destination": "team@example.com",
                                "status": "forwarded",
                                "reason": None,
                                "message_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                            }
                        ],
                    },
                    {
                        "visibility_status": "available",
                        "direction": "outbound",
                        "from": "support@inbound-mailtrap.io",
                        "delivery": {
                            "to": "customer@example.com",
                            "status": "delivered",
                            "delivered_at": "2026-05-08T11:40:05.000Z",
                            "bounced_at": None,
                        },
                    },
                    {"visibility_status": "placeholder", "direction": "inbound"},
                ],
            },
            status=200,
        )

        thread = threads_api.get_by_id(INBOX_ID, THREAD_ID)

        assert isinstance(thread, InboundThread)
        inbound, outbound, placeholder = thread.messages

        assert inbound.direction == "inbound"
        assert inbound.from_ == "customer@example.com"
        assert inbound.delivery is None
        assert inbound.forwards is not None
        assert isinstance(inbound.forwards[0], InboundForwardOutcome)
        assert inbound.forwards[0].rule_name == "Copy to support team"

        assert outbound.forwards is None
        assert isinstance(outbound.delivery, InboundThreadMessageDelivery)
        assert outbound.delivery.to == "customer@example.com"
        assert outbound.delivery.status == "delivered"
        assert outbound.delivery.delivered_at == "2026-05-08T11:40:05.000Z"
        assert outbound.delivery.bounced_at is None

        assert placeholder.delivery is None
        assert placeholder.forwards is None

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
        threads_api: InboundThreadsApi,
        status_code: int,
        response_json: dict,
        expected_error_message: str,
    ) -> None:
        responses.get(f"{BASE_URL}/{THREAD_ID}", status=status_code, json=response_json)

        with pytest.raises(APIError) as exc_info:
            threads_api.get_by_id(INBOX_ID, THREAD_ID)

        assert expected_error_message in str(exc_info.value)

    @responses.activate
    def test_delete_should_return_deleted_object(
        self, threads_api: InboundThreadsApi
    ) -> None:
        responses.delete(f"{BASE_URL}/{THREAD_ID}", status=204)

        deleted = threads_api.delete(INBOX_ID, THREAD_ID)

        assert isinstance(deleted, DeletedObject)
        assert deleted.id == THREAD_ID
