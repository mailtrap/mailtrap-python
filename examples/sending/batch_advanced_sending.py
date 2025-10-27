import base64
from pathlib import Path

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
            token=API_TOKEN,
            sandbox=True,
            inbox_id="<YOUR_INBOX_ID>",
        )
    else:
        raise ValueError(f"Invalid sending type: {type_}")


# Image should be in the same level in directory like this python file.
welcome_image = Path(__file__).parent.joinpath("welcome.png").read_bytes()

batch_mail = mt.BatchSendEmailParams(
    base=mt.BatchMail(
        sender=mt.Address(email="<SENDER_EMAIL>", name="<SENDER_NAME>"),
        cc=[mt.Address(email="cc@email.com", name="Copy to")],
        bcc=[mt.Address(email="bcc@email.com", name="Hidden Recipient")],
        subject="You are awesome!",
        text="Congrats for sending test email with Mailtrap!",
        html="""
        <!doctype html>
        <html>
          <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
          </head>
          <body style="font-family: sans-serif;">
            <div style="display: block; margin: auto; max-width: 600px;" class="main">
              <h1 style="font-size: 18px; font-weight: bold; margin-top: 20px">
                Congrats for sending test email with Mailtrap!
              </h1>
              <p>
                Inspect it using the tabs you see above and
                learn how this email can be improved.
              </p>
              <img alt="Inspect with Tabs" src="cid:welcome.png" style="width: 100%;">
              <p>
                Now send your email using our fake SMTP server
                and integration of your choice!
              </p>
              <p>Good luck! Hope it works.</p>
            </div>
            <!-- Example of invalid for email html/css, will be detected by Mailtrap: -->
            <style>
              .main { background-color: white; }
              a:hover { border-left-width: 1em; min-height: 2em; }
            </style>
          </body>
        </html>
        """,
        category="Test",
        attachments=[
            mt.Attachment(
                content=base64.b64encode(welcome_image),
                filename="welcome.png",
                disposition=mt.Disposition.INLINE,
                mimetype="image/png",
                content_id="welcome.png",
            )
        ],
        headers={"X-MT-Header": "Custom header"},
        custom_variables={"year": 2023},
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
