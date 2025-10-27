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
    else:
        raise ValueError(f"Invalid sending type: {type_}")


mail = mt.MailFromTemplate(
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


def send(client: mt.MailtrapClient, mail: mt.BaseMail) -> mt.SEND_ENDPOINT_RESPONSE:
    return client.send(mail)


if __name__ == "__main__":
    client = get_client(SendingType.DEFAULT)
    print(send(client, mail))
