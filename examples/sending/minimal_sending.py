import mailtrap as mt
from mailtrap.models.mail.mail import SendingMailResponse

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


mail = mt.Mail(
    sender=mt.Address(email="<SENDER_EMAIL>", name="<SENDER_NAME>"),
    to=[mt.Address(email="<RECEIVER_EMAIL>")],
    subject="You are awesome!",
    text="Congrats for sending test email with Mailtrap!",
)


def send(client: mt.MailtrapClient, mail: mt.BaseMail) -> mt.SEND_ENDPOINT_RESPONSE:
    return client.send(mail)


def send_via_sending_api(
    client: mt.MailtrapClient, mail: mt.BaseMail
) -> SendingMailResponse:
    """Another way to send email via Sending API"""
    return client.sending_api.send(mail)


if __name__ == "__main__":
    client = get_client(SendingType.DEFAULT)
    print(send(client, mail))
    print(send_via_sending_api(client, mail))
