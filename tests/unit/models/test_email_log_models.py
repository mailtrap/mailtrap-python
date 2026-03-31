"""Unit tests for email logs models."""

from typing import Any

from mailtrap.models.email_logs import EmailLogMessage
from mailtrap.models.email_logs import EmailLogsListFilters
from mailtrap.models.email_logs import EventDetailsBounce
from mailtrap.models.email_logs import EventDetailsClick
from mailtrap.models.email_logs import EventDetailsDelivery
from mailtrap.models.email_logs import EventDetailsOpen
from mailtrap.models.email_logs import EventDetailsUnsubscribe
from mailtrap.models.email_logs import MessageEvent
from mailtrap.models.email_logs import filter_ci_equal
from mailtrap.models.email_logs import filter_sending_domain_id_equal


class TestEmailLogMessage:
    def test_parses_list_item_with_from_key(self) -> None:
        """List response has no raw_message_url or events; those stay empty."""
        data: dict[str, Any] = {
            "message_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "status": "delivered",
            "subject": "Welcome",
            "from": "sender@example.com",
            "to": "recipient@example.com",
            "sent_at": "2025-01-15T10:30:00Z",
            "client_ip": "203.0.113.42",
            "category": "Welcome Email",
            "custom_variables": {},
            "sending_stream": "transactional",
            "sending_domain_id": 3938,
            "template_id": 100,
            "template_variables": {},
            "opens_count": 2,
            "clicks_count": 1,
        }
        msg = EmailLogMessage(**data)
        assert msg.message_id == data["message_id"]
        assert msg.from_ == "sender@example.com"
        assert msg.to == "recipient@example.com"
        assert msg.status == "delivered"
        assert msg.raw_message_url is None
        assert msg.events == []

    def test_from_api_handles_from_and_events(self) -> None:
        data: dict[str, Any] = {
            "message_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "status": "delivered",
            "subject": "Welcome",
            "from": "sender@example.com",
            "to": "recipient@example.com",
            "sent_at": "2025-01-15T10:30:00Z",
            "client_ip": None,
            "category": None,
            "custom_variables": {},
            "sending_stream": "transactional",
            "sending_domain_id": 3938,
            "template_id": None,
            "template_variables": {},
            "opens_count": 0,
            "clicks_count": 0,
            "raw_message_url": "https://example.com/raw",
            "events": None,
        }
        msg = EmailLogMessage.from_api(data)
        assert msg.from_ == "sender@example.com"
        assert msg.raw_message_url == "https://example.com/raw"
        assert msg.events == []

    def test_from_api_parses_events_with_deterministic_details_type(self) -> None:
        """event_type selects correct EventDetails* (open vs unsubscribe same shape)."""
        # open and unsubscribe both have web_ip_address; selection is by event_type
        data: dict[str, Any] = {
            "message_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "status": "delivered",
            "subject": "Welcome",
            "from": "sender@example.com",
            "to": "recipient@example.com",
            "sent_at": "2025-01-15T10:30:00Z",
            "client_ip": None,
            "category": None,
            "custom_variables": {},
            "sending_stream": "transactional",
            "sending_domain_id": 3938,
            "template_id": None,
            "template_variables": {},
            "opens_count": 0,
            "clicks_count": 0,
            "raw_message_url": None,
            "events": [
                {
                    "event_type": "open",
                    "created_at": "2025-01-15T10:35:00Z",
                    "details": {"web_ip_address": "198.51.100.50"},
                },
                {
                    "event_type": "unsubscribe",
                    "created_at": "2025-01-15T10:40:00Z",
                    "details": {"web_ip_address": "198.51.100.50"},
                },
            ],
        }
        msg = EmailLogMessage.from_api(data)
        assert len(msg.events) == 2
        assert msg.events[0].event_type == "open"
        assert isinstance(msg.events[0].details, EventDetailsOpen)
        assert msg.events[0].details.web_ip_address == "198.51.100.50"
        assert msg.events[1].event_type == "unsubscribe"
        assert isinstance(msg.events[1].details, EventDetailsUnsubscribe)
        assert msg.events[1].details.web_ip_address == "198.51.100.50"

    def test_from_api_parses_click_and_bounce_events(self) -> None:
        """Click and bounce events get EventDetailsClick and EventDetailsBounce."""
        data: dict[str, Any] = {
            "message_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "status": "delivered",
            "subject": "Welcome",
            "from": "sender@example.com",
            "to": "recipient@example.com",
            "sent_at": "2025-01-15T10:30:00Z",
            "client_ip": None,
            "category": None,
            "custom_variables": {},
            "sending_stream": "transactional",
            "sending_domain_id": 3938,
            "template_id": None,
            "template_variables": {},
            "opens_count": 0,
            "clicks_count": 1,
            "raw_message_url": None,
            "events": [
                {
                    "event_type": "click",
                    "created_at": "2025-01-15T10:35:00Z",
                    "details": {
                        "click_url": "https://example.com/track/abc",
                        "web_ip_address": "198.51.100.50",
                    },
                },
                {
                    "event_type": "bounce",
                    "created_at": "2025-01-15T10:36:00Z",
                    "details": {
                        "email_service_provider_response": "User unknown",
                        "bounce_category": "invalid_recipient",
                    },
                },
            ],
        }
        msg = EmailLogMessage.from_api(data)
        assert len(msg.events) == 2
        assert isinstance(msg.events[0].details, EventDetailsClick)
        assert msg.events[0].details.click_url == "https://example.com/track/abc"
        assert isinstance(msg.events[1].details, EventDetailsBounce)
        assert msg.events[1].details.bounce_category == "invalid_recipient"

    def test_from_api_parses_delivery_event(self) -> None:
        """Delivery event gets EventDetailsDelivery."""
        data: dict[str, Any] = {
            "message_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "status": "delivered",
            "subject": "Welcome",
            "from": "sender@example.com",
            "to": "recipient@example.com",
            "sent_at": "2025-01-15T10:30:00Z",
            "client_ip": None,
            "category": None,
            "custom_variables": {},
            "sending_stream": "transactional",
            "sending_domain_id": 3938,
            "template_id": None,
            "template_variables": {},
            "opens_count": 0,
            "clicks_count": 0,
            "raw_message_url": None,
            "events": [
                {
                    "event_type": "delivery",
                    "created_at": "2025-01-15T10:31:00Z",
                    "details": {
                        "email_service_provider": "Google",
                        "recipient_mx": "gmail-smtp-in.l.google.com",
                    },
                },
            ],
        }
        msg = EmailLogMessage.from_api(data)
        assert len(msg.events) == 1
        assert isinstance(msg.events[0], MessageEvent)
        assert msg.events[0].event_type == "delivery"
        assert isinstance(msg.events[0].details, EventDetailsDelivery)
        assert msg.events[0].details.email_service_provider == "Google"


class TestEmailLogsListFilters:
    def test_to_params_date_range(self) -> None:
        f = EmailLogsListFilters(
            sent_after="2025-01-01T00:00:00Z",
            sent_before="2025-01-31T23:59:59Z",
        )
        params = f.to_params()
        assert params["filters[sent_after]"] == "2025-01-01T00:00:00Z"
        assert params["filters[sent_before]"] == "2025-01-31T23:59:59Z"

    def test_to_params_with_to_and_sending_domain_id(self) -> None:
        f = EmailLogsListFilters(
            to=filter_ci_equal("recipient@example.com"),
            sending_domain_id=filter_sending_domain_id_equal([3938, 3939]),
        )
        params = f.to_params()
        assert params["filters[to][operator]"] == "ci_equal"
        assert params["filters[to][value]"] == "recipient@example.com"
        assert params["filters[sending_domain_id][operator]"] == "equal"
        assert params["filters[sending_domain_id][value][]"] == [3938, 3939]
