import json

import pytest
import responses

import mailtrap as mt
from mailtrap.api.sending import SendingApi
from mailtrap.config import SENDING_HOST
from mailtrap.http import HttpClient
from mailtrap.models.mail import SendingMailResponse
from mailtrap.models.mail.batch_mail import BatchEmailRequest
from mailtrap.models.mail.batch_mail import BatchMail
from mailtrap.models.mail.batch_mail import BatchSendEmailParams
from mailtrap.models.mail.batch_mail import BatchSendResponse

ACCOUNT_ID = "321"
PROJECT_ID = 123
INBOX_ID = "456"

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

DUMMY_BATCH_MAIL = BatchMail(
    sender=DUMMY_ADDRESS,
    subject="Batch Email Subject",
    text="Batch email text",
    html="<p>Batch email HTML</p>",
)

DUMMY_BATCH_REQUEST = BatchEmailRequest(
    to=[DUMMY_ADDRESS],
    subject="Individual Email Subject",
    text="Individual email text",
)

DUMMY_BATCH_PARAMS = BatchSendEmailParams(
    base=DUMMY_BATCH_MAIL,
    requests=[DUMMY_BATCH_REQUEST],
)

SEND_FULL_URL = f"https://{SENDING_HOST}/api/send"
BATCH_SEND_FULL_URL = f"https://{SENDING_HOST}/api/batch"


def get_sending_api() -> SendingApi:
    return SendingApi(client=HttpClient(SENDING_HOST))


class TestSendingApi:

    @responses.activate
    @pytest.mark.parametrize("mail", MAIL_ENTITIES)
    def test_send_should_raise_authorization_error(
        self,
        mail: mt.BaseMail,
    ) -> None:
        response_body = {"errors": ["Unauthorized"]}
        responses.post(SEND_FULL_URL, json=response_body, status=401)
        api = get_sending_api()

        with pytest.raises(mt.AuthorizationError):
            api.send(mail)

    @responses.activate
    @pytest.mark.parametrize("mail", MAIL_ENTITIES)
    def test_send_should_raise_api_error_for_400_status_code(
        self,
        mail: mt.BaseMail,
    ) -> None:
        response_body = {"errors": ["Some error msg"]}
        responses.post(SEND_FULL_URL, json=response_body, status=400)

        api = get_sending_api()

        with pytest.raises(mt.APIError):
            api.send(mail)

    @responses.activate
    @pytest.mark.parametrize("mail", MAIL_ENTITIES)
    def test_send_should_raise_api_error_for_500_status_code(
        self,
        mail: mt.BaseMail,
    ) -> None:
        response_body = {"errors": ["Some error msg"]}
        responses.post(SEND_FULL_URL, json=response_body, status=500)

        api = get_sending_api()

        with pytest.raises(mt.APIError):
            api.send(mail)

    @responses.activate
    @pytest.mark.parametrize("mail", MAIL_ENTITIES)
    def test_send_should_handle_success_response(
        self,
        mail: mt.BaseMail,
    ) -> None:
        response_body = {"success": True, "message_ids": ["12345"]}
        responses.post(SEND_FULL_URL, json=response_body)

        api = get_sending_api()
        result = api.send(mail)

        assert isinstance(result, SendingMailResponse)
        assert result.success is True
        assert len(responses.calls) == 1
        request = responses.calls[0].request  # type: ignore
        assert request.body == json.dumps(mail.api_data).encode()

    @responses.activate
    def test_batch_send_should_raise_authorization_error(self) -> None:
        response_body = {"errors": ["Unauthorized"]}
        responses.post(BATCH_SEND_FULL_URL, json=response_body, status=401)
        api = get_sending_api()

        with pytest.raises(mt.AuthorizationError):
            api.batch_send(DUMMY_BATCH_PARAMS)

    @responses.activate
    def test_batch_send_should_raise_api_error_for_400_status_code(self) -> None:
        response_body = {"errors": ["Some error msg"]}
        responses.post(BATCH_SEND_FULL_URL, json=response_body, status=400)

        api = get_sending_api()

        with pytest.raises(mt.APIError):
            api.batch_send(DUMMY_BATCH_PARAMS)

    @responses.activate
    def test_batch_send_should_raise_api_error_for_500_status_code(self) -> None:
        response_body = {"errors": ["Some error msg"]}
        responses.post(BATCH_SEND_FULL_URL, json=response_body, status=500)

        api = get_sending_api()

        with pytest.raises(mt.APIError):
            api.batch_send(DUMMY_BATCH_PARAMS)

    @responses.activate
    def test_batch_send_should_handle_success_response(self) -> None:
        response_body = {
            "success": True,
            "responses": [{"success": True, "message_ids": ["12345"]}],
        }
        responses.post(BATCH_SEND_FULL_URL, json=response_body)

        api = get_sending_api()
        result = api.batch_send(DUMMY_BATCH_PARAMS)

        assert isinstance(result, BatchSendResponse)
        assert result.success is True
        assert len(result.responses) == 1
        assert result.responses[0].success is True
        assert result.responses[0].message_ids == ["12345"]
        assert len(responses.calls) == 1
        request = responses.calls[0].request  # type: ignore
        assert request.body == json.dumps(DUMMY_BATCH_PARAMS.api_data).encode()

    @responses.activate
    def test_batch_send_should_handle_partial_failure_response(self) -> None:
        response_body = {
            "success": True,
            "responses": [
                {"success": True, "message_ids": ["12345"]},
                {"success": False, "errors": ["Invalid email address"]},
            ],
        }
        responses.post(BATCH_SEND_FULL_URL, json=response_body)

        api = get_sending_api()
        result = api.batch_send(DUMMY_BATCH_PARAMS)

        assert isinstance(result, BatchSendResponse)
        assert result.success is True
        assert len(result.responses) == 2
        assert result.responses[0].success is True
        assert result.responses[0].message_ids == ["12345"]
        assert result.responses[1].success is False
        assert result.responses[1].errors == ["Invalid email address"]
