import mailtrap as mt

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


batch_mail = mt.BatchSendEmailParams(
    base=mt.BatchMail(
        sender=mt.Address(email="<SENDER_EMAIL>", name="<SENDER_NAME>"),
        subject="You are awesome!",
        text="Congrats for sending test email with Mailtrap!",
        category="Integration Test",
    ),
    requests=[
        mt.BatchEmailRequest(
            to=[mt.Address(email="<RECEIVER_EMAIL>")],
        ),
    ],
)


def batch_send(
    client: mt.MailtrapClient,
    mail: mt.BatchSendEmailParams,
) -> mt.BATCH_SEND_ENDPOINT_RESPONSE:
    return client.batch_send(mail)


if __name__ == "__main__":
    client = get_client(SendingType.DEFAULT)
    print(batch_send(client, batch_mail))
