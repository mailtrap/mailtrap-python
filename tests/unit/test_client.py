from typing import Any

import pytest

import mailtrap as mt

DUMMY_ADDRESS = mt.Address(email="joe@mail.com")
DUMMY_MAIL = mt.Mail(
    sender=DUMMY_ADDRESS,
    to=[DUMMY_ADDRESS],
    subject="Email subject",
    text="email text",
)
DUMMY_MAIL_FROM_TEMPLATE = mt.MailFromTemplate(
    sender=DUMMY_ADDRESS,
    to=[DUMMY_ADDRESS],
    template_uuid="fake_uuid",
)

MAIL_ENTITIES = [DUMMY_MAIL, DUMMY_MAIL_FROM_TEMPLATE]


class TestMailtrapClient:
    SEND_URL = "https://send.api.mailtrap.io:443/api/send"

    @staticmethod
    def get_client(**kwargs: Any) -> mt.MailtrapClient:
        props = {"token": "fake_token", **kwargs}
        return mt.MailtrapClient(**props)

    @pytest.mark.parametrize(
        "arguments",
        [
            {"sandbox": True},
            {"inbox_id": "12345"},
            {"bulk": True, "sandbox": True, "inbox_id": "12345"},
        ],
    )
    def test_client_validation(self, arguments: dict[str, Any]) -> None:
        with pytest.raises(mt.ClientConfigurationError):
            self.get_client(**arguments)

    def test_get_testing_api_validation(self) -> None:
        client = self.get_client()
        with pytest.raises(mt.ClientConfigurationError) as exc_info:
            _ = client.testing_api

        assert "`account_id` is required for Testing API" in str(exc_info.value)

    @pytest.mark.parametrize(
        "arguments, expected_url",
        [
            ({}, "https://send.api.mailtrap.io:443/api/send"),
            (
                {"api_host": "example.send.com", "api_port": 543},
                "https://example.send.com:543/api/send",
            ),
            (
                {"api_host": "example.send.com", "sandbox": True, "inbox_id": "12345"},
                "https://example.send.com:443/api/send/12345",
            ),
            (
                {"api_host": "example.send.com", "bulk": True},
                "https://example.send.com:443/api/send",
            ),
            (
                {"sandbox": True, "inbox_id": "12345"},
                "https://sandbox.api.mailtrap.io:443/api/send/12345",
            ),
            (
                {"bulk": True},
                "https://bulk.api.mailtrap.io:443/api/send",
            ),
        ],
    )
    def test_api_send_url_should_return_default_sending_url(
        self, arguments: dict[str, Any], expected_url: str
    ) -> None:
        client = self.get_client(**arguments)

        assert client.api_send_url == expected_url

    def test_headers_should_return_appropriate_dict(self) -> None:
        client = self.get_client()

        assert client.headers == {
            "Authorization": "Bearer fake_token",
            "Content-Type": "application/json",
            "User-Agent": mt.MailtrapClient.DEFAULT_USER_AGENT,
        }

    def test_headers_should_use_custom_user_agent_when_provided(self) -> None:
        custom_ua = "MyApp/1.0 (custom)"
        client = self.get_client(user_agent=custom_ua)

        assert client.headers["User-Agent"] == custom_ua
