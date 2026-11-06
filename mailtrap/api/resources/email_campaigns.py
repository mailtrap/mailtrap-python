from typing import Optional

from mailtrap.http import HttpClient
from mailtrap.models.common import DeletedObject
from mailtrap.models.email_campaigns import CreateEmailCampaignParams
from mailtrap.models.email_campaigns import EmailCampaign
from mailtrap.models.email_campaigns import EmailCampaignListParams
from mailtrap.models.email_campaigns import EmailCampaignListResponse
from mailtrap.models.email_campaigns import EmailCampaignResponse
from mailtrap.models.email_campaigns import EmailCampaignStats
from mailtrap.models.email_campaigns import EmailCampaignStatsParams
from mailtrap.models.email_campaigns import EmailCampaignStatsResponse
from mailtrap.models.email_campaigns import ScheduleEmailCampaignParams
from mailtrap.models.email_campaigns import UpdateEmailCampaignParams


class EmailCampaignsApi:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def get_list(
        self, params: Optional[EmailCampaignListParams] = None
    ) -> EmailCampaignListResponse:
        """
        List email campaigns for the account, newest first. ``params`` filters
        by name and paginates the result; omit it for the first page with API
        defaults.
        """
        query_params = params.api_query_params if params else None
        response = self._client.get(self._api_path(), params=query_params or None)
        return EmailCampaignListResponse(**response)

    def get_by_id(self, email_campaign_id: int) -> EmailCampaign:
        """
        Get a single email campaign by id.
        """
        response = self._client.get(self._api_path(email_campaign_id))
        return EmailCampaignResponse(**response).data

    def create(self, campaign_params: CreateEmailCampaignParams) -> EmailCampaign:
        """
        Create a new email campaign in the ``draft`` state. The campaign must
        reference an existing domain via ``domain_id`` and
        include a template ``subject`` within ``template_attributes``.
        """
        response = self._client.post(self._api_path(), json=campaign_params.api_data)
        return EmailCampaignResponse(**response).data

    def update(
        self, email_campaign_id: int, campaign_params: UpdateEmailCampaignParams
    ) -> EmailCampaign:
        """
        Update an existing ``draft`` email campaign. Only the fields supplied
        in ``campaign_params`` are sent to the API.
        """
        response = self._client.patch(
            self._api_path(email_campaign_id),
            json=campaign_params.api_data,
        )
        return EmailCampaignResponse(**response).data

    def delete(self, email_campaign_id: int) -> DeletedObject:
        """
        Delete an email campaign. Only a campaign in the ``draft`` state can be
        deleted.
        """
        self._client.delete(self._api_path(email_campaign_id))
        return DeletedObject(email_campaign_id)

    def start(self, email_campaign_id: int) -> EmailCampaign:
        """
        Start sending a ``draft`` campaign immediately.
        """
        return self._action(email_campaign_id, "start")

    def schedule(
        self, email_campaign_id: int, schedule_params: ScheduleEmailCampaignParams
    ) -> EmailCampaign:
        """
        Schedule a ``draft`` campaign to start sending at a future time. The
        time is reported back in ``current_state_metadata.scheduled_at``.
        """
        response = self._client.post(
            f"{self._api_path(email_campaign_id)}/schedule",
            json=schedule_params.api_data,
        )
        return EmailCampaignResponse(**response).data

    def cancel(self, email_campaign_id: int) -> EmailCampaign:
        """
        Cancel a ``scheduled`` campaign, returning it to the ``draft`` state.
        """
        return self._action(email_campaign_id, "cancel")

    def terminate(self, email_campaign_id: int) -> EmailCampaign:
        """
        Terminate a campaign that is currently sending (``started``,
        ``queued``, or ``paused``), aborting the in-flight send.
        """
        return self._action(email_campaign_id, "terminate")

    def reset(self, email_campaign_id: int) -> EmailCampaign:
        """
        Reset a ``scheduled`` campaign back to the ``draft`` state.
        """
        return self._action(email_campaign_id, "reset")

    def get_stats(
        self,
        email_campaign_id: int,
        params: Optional[EmailCampaignStatsParams] = None,
    ) -> EmailCampaignStats:
        """
        Get aggregated performance statistics for a single campaign. If the
        campaign has never been started, all counts and rates are ``0``.
        ``params`` narrows the aggregation window; omit it to cover the whole
        period since the campaign was last started.
        """
        query_params = params.api_query_params if params else None
        response = self._client.get(
            f"{self._api_path(email_campaign_id)}/stats", params=query_params or None
        )
        return EmailCampaignStatsResponse(**response).data

    def _action(self, email_campaign_id: int, action: str) -> EmailCampaign:
        response = self._client.post(f"{self._api_path(email_campaign_id)}/{action}")
        return EmailCampaignResponse(**response).data

    def _api_path(self, email_campaign_id: Optional[int] = None) -> str:
        path = "/api/email_campaigns"
        if email_campaign_id is not None:
            return f"{path}/{email_campaign_id}"
        return path
