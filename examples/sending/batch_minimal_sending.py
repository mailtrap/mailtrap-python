import mailtrap as mt
from mailtrap.models.mail.batch_mail import BatchSendResponse

API_TOKEN = "<YOUR_API_TOKEN>"


class SendingType:
    DEFAULT = "default"
    BULK = "bulk"
    SANDBOX = "sandbox"


def get_client(type_: SendingType) -> mt.MailtrapClient:
    if type_ == SendingType.DEFAULT:
        return mt.MailtrapClient(token=API_TOKEN)
    elif type_ == SendingType.BULK:
        return mt.MailtrapClient(token=API_TOKEN, bulk=True)
    elif type_ == SendingType.SANDBOX:
        return mt.MailtrapClient(
            token=API_TOKEN, sandbox=True, inbox_id="<YOUR_INBOX_ID>"
        )
    raise ValueError(f"Invalid sending type: {type_}")


batch_mail = mt.BatchSendEmailParams(
    base=mt.BatchMail(
        sender=mt.Address(email="<SENDER_EMAIL>", name="<SENDER_NAME>"),
        subject="You are awesome!",
        text="Congrats for sending test email with Mailtrap!",
        category="Integration Test",
    ),
    requests=[
        mt.BatchEmailRequest(
            to=[mt.Address(email="<RECEIVER_EMAIL_1>")],
        ),
        mt.BatchEmailRequest(
            to=[mt.Address(email="<RECEIVER_EMAIL_2>")],
        ),
    ],
)


def batch_send(
    client: mt.MailtrapClient,
    mail: mt.BatchSendEmailParams,
) -> mt.BATCH_SEND_ENDPOINT_RESPONSE:
    return client.batch_send(mail)


def batch_send_via_sending_api(
    client: mt.MailtrapClient, mail: mt.BatchSendEmailParams
) -> BatchSendResponse:
    """Another way to batch_send email via Sending API"""
    return client.sending_api.batch_send(mail)


if __name__ == "__main__":
    client = get_client(SendingType.DEFAULT)
    print(batch_send(client, batch_mail))
    print(batch_send_via_sending_api(client, batch_mail))
