from typing import Optional

from mailtrap.http import HttpClient
from mailtrap.models.email_campaigns import CreateEmailCampaignParams
from mailtrap.models.email_campaigns import EmailCampaign
from mailtrap.models.email_campaigns import EmailCampaignListParams
from mailtrap.models.email_campaigns import EmailCampaignListResponse
from mailtrap.models.email_campaigns import EmailCampaignStats
from mailtrap.models.email_campaigns import UpdateEmailCampaignParams


class EmailCampaignsApi:
    def __init__(self, client: HttpClient, account_id: str) -> None:
        self._account_id = account_id
        self._client = client

    def get_list(
        self,
        per_page: Optional[int] = None,
        search: Optional[str] = None,
        token: Optional[int] = None,
    ) -> EmailCampaignListResponse:
        """
        List email campaigns for the account, newest first. ``search`` filters
        by name (case-insensitive partial match), ``per_page`` sets the page
        size (max 100, default 50), and ``token`` is the page number to
        retrieve (default 1).
        """
        params = EmailCampaignListParams(
            per_page=per_page, search=search, token=token
        ).api_query_params
        response = self._client.get(self._api_path(), params=params or None)
        return EmailCampaignListResponse(**response)

    def get_by_id(self, email_campaign_id: int) -> EmailCampaign:
        """
        Get a single email campaign by id.
        """
        response = self._client.get(self._api_path(email_campaign_id))
        return EmailCampaign(**response)

    def create(self, campaign_params: CreateEmailCampaignParams) -> EmailCampaign:
        """
        Create a new email campaign in the ``draft`` state. The campaign must
        reference an existing sending domain via ``mailsend_domain_id``.
        """
        response = self._client.post(
            self._api_path(), json={"email_campaign": campaign_params.api_data}
        )
        return EmailCampaign(**response)

    def update(
        self, email_campaign_id: int, campaign_params: UpdateEmailCampaignParams
    ) -> EmailCampaign:
        """
        Update an existing email campaign. The campaign must not be in a
        sending state. Only the fields supplied in ``campaign_params`` are sent
        to the API.
        """
        response = self._client.patch(
            self._api_path(email_campaign_id),
            json={"email_campaign": campaign_params.api_data},
        )
        return EmailCampaign(**response)

    def delete(self, email_campaign_id: int) -> EmailCampaign:
        """
        Delete an email campaign. The campaign must not be in a sending state.
        The deleted campaign object is returned (HTTP 200 + body, not 204).
        """
        response = self._client.delete(self._api_path(email_campaign_id))
        return EmailCampaign(**response)

    def get_stats(self, email_campaign_id: int) -> EmailCampaignStats:
        """
        Get aggregated performance statistics for a single campaign. If the
        campaign has never been started, all counts and rates are ``0``.
        """
        response = self._client.get(f"{self._api_path(email_campaign_id)}/stats")
        return EmailCampaignStats(**response)

    def _api_path(self, email_campaign_id: Optional[int] = None) -> str:
        # The Email Campaigns endpoint is token-scoped, NOT account-scoped:
        # the account is resolved from the API token server-side.
        path = "/api/email_campaigns"
        if email_campaign_id is not None:
            return f"{path}/{email_campaign_id}"
        return path
