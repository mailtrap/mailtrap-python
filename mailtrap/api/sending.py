from typing import Optional

from mailtrap.http import HttpClient
from mailtrap.models.mail import BaseMail
from mailtrap.models.mail import SendingMailResponse
from mailtrap.models.mail.batch_mail import BatchSendEmailParams
from mailtrap.models.mail.batch_mail import BatchSendResponse


class SendingApi:
    def __init__(self, client: HttpClient, inbox_id: Optional[str] = None) -> None:
        self._inbox_id = inbox_id
        self._client = client

    def _get_api_url(self, base_url: str) -> str:
        if self._inbox_id:
            return f"{base_url}/{self._inbox_id}"
        return base_url

    def send(self, mail: BaseMail) -> SendingMailResponse:
        """Send email (text, html, text&html, templates)."""
        response = self._client.post(self._get_api_url("/api/send"), json=mail.api_data)
        return SendingMailResponse(**response)

    def batch_send(self, mail: BatchSendEmailParams) -> BatchSendResponse:
        """
        Batch send email (text, html, text&html, templates). Please note that
        the endpoint will return a 200-level http status, even when sending
        for individual messages may fail. Users of this endpoint should check
        the success and errors for each message in the response (the results
        are ordered the same as the original messages - requests). Please note
        that the endpoint accepts up to 500 messages per API call, and up to 50 MB
        payload size, including attachments.
        """
        response = self._client.post(self._get_api_url("/api/batch"), json=mail.api_data)
        return BatchSendResponse(**response)
