from typing import Optional

from mailtrap._deprecation import renamed_kwargs
from mailtrap.http import HttpClient
from mailtrap.models.common import DeletedObject
from mailtrap.models.domains import CreateDomainParams
from mailtrap.models.domains import Domain
from mailtrap.models.domains import SendSetupInstructionsParams
from mailtrap.models.domains import SendSetupInstructionsResponse
from mailtrap.models.domains import UpdateDomainParams


class DomainsApi:
    def __init__(self, client: HttpClient, account_id: str) -> None:
        self._account_id = account_id
        self._client = client

    def get_list(self) -> list[Domain]:
        """
        Get domains and their statuses.
        """
        response = self._client.get(self._api_path())
        domains = response.get("data", [])
        return [Domain(**domain) for domain in domains]

    @renamed_kwargs(sending_domain_id="domain_id")
    def get_by_id(self, domain_id: int) -> Domain:
        """
        Get domain data and its status.
        """
        response = self._client.get(self._api_path(domain_id))
        return Domain(**response)

    def create(self, domain_params: CreateDomainParams) -> Domain:
        """
        Create a domain. To later check the status of the newly created domain,
        review the compliance_status and dns_verified fields in the response
        of the Get domain by ID or Get domains endpoints.
        """
        response = self._client.post(
            self._api_path(), json={"sending_domain": domain_params.api_data}
        )
        return Domain(**response)

    @renamed_kwargs(sending_domain_id="domain_id")
    def update(self, domain_id: int, domain_params: UpdateDomainParams) -> Domain:
        """
        Update configuration settings for a domain. Only the fields
        supplied in `domain_params` are sent to the API.
        """
        response = self._client.patch(
            self._api_path(domain_id),
            json={"sending_domain": domain_params.api_data},
        )
        return Domain(**response)

    @renamed_kwargs(sending_domain_id="domain_id")
    def delete(self, domain_id: int) -> DeletedObject:
        """
        Delete a domain.
        """
        self._client.delete(self._api_path(domain_id))
        return DeletedObject(id=domain_id)

    @renamed_kwargs(sending_domain_id="domain_id")
    def send_setup_instructions(
        self,
        domain_id: int,
        instructions_params: SendSetupInstructionsParams,
    ) -> SendSetupInstructionsResponse:
        """
        Send domain setup instructions.
        """
        self._client.post(
            f"{self._api_path(domain_id)}/send_setup_instructions",
            json=instructions_params.api_data,
        )
        return SendSetupInstructionsResponse(
            message="Instructions email has been sent successfully"
        )

    def _api_path(self, domain_id: Optional[int] = None) -> str:
        path = f"/api/accounts/{self._account_id}/sending_domains"
        if domain_id is not None:
            path = f"{path}/{domain_id}"
        return path
