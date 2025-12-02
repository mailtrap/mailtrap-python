from typing import Optional

from mailtrap.http import HttpClient
from mailtrap.models.common import DeletedObject
from mailtrap.models.sending_domains import CreateSendingDomainParams
from mailtrap.models.sending_domains import SendingDomain
from mailtrap.models.sending_domains import SendSetupInstructionsParams
from mailtrap.models.sending_domains import SendSetupInstructionsResponse


class SendingDomainsApi:
    def __init__(self, client: HttpClient, account_id: str) -> None:
        self._account_id = account_id
        self._client = client

    def get_list(self) -> list[SendingDomain]:
        """
        Get sending domains and their statuses.
        """
        response = self._client.get(self._api_path())
        domains = response.get("data", [])
        return [SendingDomain(**domain) for domain in domains]

    def get_by_id(self, sending_domain_id: int) -> SendingDomain:
        """
        Get domain data and its status.
        """
        response = self._client.get(self._api_path(sending_domain_id))
        return SendingDomain(**response)

    def create(self, domain_params: CreateSendingDomainParams) -> SendingDomain:
        """
        Create a sending domain. To later check the status of the newly created domain,
        review the compliance_status and dns_verified fields in the response
        of the Get domain by ID or Get sending domains endpoints.
        """
        response = self._client.post(
            self._api_path(), json={"sending_domain": domain_params.api_data}
        )
        return SendingDomain(**response)

    def delete(self, sending_domain_id: int) -> DeletedObject:
        """
        Delete a sending domain.
        """
        self._client.delete(self._api_path(sending_domain_id))
        return DeletedObject(id=sending_domain_id)

    def send_setup_instructions(
        self,
        sending_domain_id: int,
        instructions_params: SendSetupInstructionsParams,
    ) -> SendSetupInstructionsResponse:
        """
        Send sending domain setup instructions.
        """
        self._client.post(
            f"{self._api_path(sending_domain_id)}/send_setup_instructions",
            json=instructions_params.api_data,
        )
        return SendSetupInstructionsResponse(
            message="Instructions email has been sent successfully"
        )

    def _api_path(self, sending_domain_id: Optional[int] = None) -> str:
        path = f"/api/accounts/{self._account_id}/sending_domains"
        if sending_domain_id is not None:
            path = f"{path}/{sending_domain_id}"
        return path
