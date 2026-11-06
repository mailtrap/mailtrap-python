import os

import mailtrap as mt
from mailtrap.models.common import DeletedObject
from mailtrap.models.domains import Domain
from mailtrap.models.domains import SendSetupInstructionsResponse

API_KEY = os.environ["MAILTRAP_API_KEY"]
ACCOUNT_ID = os.environ["MAILTRAP_ACCOUNT_ID"]

client = mt.MailtrapClient(token=API_KEY, account_id=ACCOUNT_ID)
domains_api = client.domains_api.domains


def list_domains() -> list[Domain]:
    return domains_api.get_list()


def get_domain(domain_id: int) -> Domain:
    return domains_api.get_by_id(domain_id)


def create_domain(domain_name: str) -> Domain:
    params = mt.CreateDomainParams(domain_name=domain_name)
    return domains_api.create(params)


def update_domain(domain_id: int) -> Domain:
    params = mt.UpdateDomainParams(
        open_tracking_enabled=True,
        click_tracking_enabled=True,
        tracking_opt_out_enabled=True,
        auto_unsubscribe_link_enabled=False,
        inbound_enabled=False,
    )
    return domains_api.update(domain_id, params)


def delete_domain(domain_id: int) -> DeletedObject:
    return domains_api.delete(domain_id)


def send_setup_instructions(domain_id: int, email: str) -> SendSetupInstructionsResponse:
    params = mt.SendSetupInstructionsParams(email=email)
    return domains_api.send_setup_instructions(domain_id, params)


if __name__ == "__main__":
    new_domain = create_domain("example.com")
    print(new_domain)

    domains = list_domains()
    print(domains)

    domain = get_domain(new_domain.id)
    print(domain)

    updated_domain = update_domain(new_domain.id)
    print(updated_domain)

    response = send_setup_instructions(new_domain.id, "example@mail.com")
    print(response)

    deleted_domain = delete_domain(new_domain.id)
    print(deleted_domain)
