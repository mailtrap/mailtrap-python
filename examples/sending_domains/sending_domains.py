import mailtrap as mt
from mailtrap.models.common import DeletedObject
from mailtrap.models.sending_domains import SendingDomain
from mailtrap.models.sending_domains import SendSetupInstructionsResponse

API_TOKEN = "YOUR_API_TOKEN"
ACCOUNT_ID = "YOUR_ACCOUNT_ID"

client = mt.MailtrapClient(token=API_TOKEN, account_id=ACCOUNT_ID)
sending_domains_api = client.sending_domains_api.sending_domains


def list_sending_domains() -> list[SendingDomain]:
    return sending_domains_api.get_list()


def get_sending_domain(domain_id: int) -> SendingDomain:
    return sending_domains_api.get_by_id(domain_id)


def create_sending_domain(domain_name: str) -> SendingDomain:
    params = mt.CreateSendingDomainParams(domain_name=domain_name)
    return sending_domains_api.create(params)


def delete_sending_domain(domain_id: int) -> DeletedObject:
    return sending_domains_api.delete(domain_id)


def send_setup_instructions(domain_id: int, email: str) -> SendSetupInstructionsResponse:
    params = mt.SendSetupInstructionsParams(email=email)
    return sending_domains_api.send_setup_instructions(domain_id, params)


if __name__ == "__main__":
    new_domain = create_sending_domain("example.com")
    print(new_domain)

    domains = list_sending_domains()
    print(domains)

    domain = get_sending_domain(new_domain.id)
    print(domain)

    response = send_setup_instructions(new_domain.id, "example@mail.com")
    print(response)

    deleted_domain = delete_sending_domain(new_domain.id)
    print(deleted_domain)
