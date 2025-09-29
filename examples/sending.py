import mailtrap as mt

API_TOKEN = "<YOUR_API_TOKEN>"
INBOX_ID = "<YOUR_INBOX_ID>"


default_client = mt.MailtrapClient(token=API_TOKEN)
bulk_client = mt.MailtrapClient(token=API_TOKEN, bulk=True)
sandbox_client = mt.MailtrapClient(token=API_TOKEN, sandbox=True, inbox_id=INBOX_ID)


mail = mt.Mail(
    sender=mt.Address(email="<SENDER_EMAIL>", name="<SENDER_NAME>"),
    to=[mt.Address(email="<RECEIVER_EMAIL>")],
    subject="You are awesome!",
    text="Congrats for sending test email with Mailtrap!",
    category="Integration Test",
)
mail_from_template = mt.MailFromTemplate(
    sender=mt.Address(email="<SENDER_EMAIL>", name="<SENDER_NAME>"),
    to=[mt.Address(email="<RECEIVER_EMAIL>")],
    template_uuid="<YOUR_TEMPLATE_UUID>",
    template_variables={
        "company_info_name": "Test_Company_info_name",
        "name": "Test_Name",
        "company_info_address": "Test_Company_info_address",
        "company_info_city": "Test_Company_info_city",
        "company_info_zip_code": "Test_Company_info_zip_code",
        "company_info_country": "Test_Company_info_country",
    },
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

batch_mail_from_template = mt.BatchSendEmailParams(
    base=mt.BatchMailFromTemplate(
        sender=mt.Address(email="<SENDER_EMAIL>", name="<SENDER_NAME>"),
        template_uuid="<YOUR_TEMPLATE_UUID>",
        template_variables={
            "company_info_name": "Test_Company_info_name",
            "name": "Test_Name",
            "company_info_address": "Test_Company_info_address",
            "company_info_city": "Test_Company_info_city",
            "company_info_zip_code": "Test_Company_info_zip_code",
            "company_info_country": "Test_Company_info_country",
        },
    ),
    requests=[
        mt.BatchEmailRequest(
            to=[mt.Address(email="<RECEIVER_EMAIL>")],
            subject="You are awesome!",
            text="Congrats for sending test email with Mailtrap!",
            category="Integration Test",
        ),
    ],
)


def send(client: mt.MailtrapClient, mail: mt.BaseMail) -> mt.SEND_ENDPOINT_RESPONSE:
    return client.send(mail)


def batch_send(
    client: mt.MailtrapClient, mail: mt.BatchSendEmailParams
) -> mt.BATCH_SEND_ENDPOINT_RESPONSE:
    return client.batch_send(mail=mail)


if __name__ == "__main__":
    print(send(default_client, mail))
    print(batch_send(default_client, batch_mail))
