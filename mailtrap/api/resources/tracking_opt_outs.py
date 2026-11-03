from typing import Optional

from mailtrap.http import HttpClient
from mailtrap.models.tracking_opt_outs import CreateTrackingOptOutParams
from mailtrap.models.tracking_opt_outs import TrackingOptOut
from mailtrap.models.tracking_opt_outs import TrackingOptOutResponse
from mailtrap.models.tracking_opt_outs import TrackingOptOutsListParams
from mailtrap.models.tracking_opt_outs import TrackingOptOutsListResponse


class TrackingOptOutsApi:
    def __init__(self, client: HttpClient) -> None:
        self._client = client

    def get_list(
        self, params: Optional[TrackingOptOutsListParams] = None
    ) -> TrackingOptOutsListResponse:
        """
        List email addresses that have opted out of open and click tracking.
        The endpoint returns up to 1000 records per request; pass the previous
        response's `last_id` to fetch the next page.
        """
        query_params = params.api_query_params if params is not None else None
        response = self._client.get(self._api_path(), params=query_params)
        return TrackingOptOutsListResponse(**response)

    def create(self, params: CreateTrackingOptOutParams) -> TrackingOptOut:
        """
        Add an email address to the tracking opt-out list for a domain.
        """
        response = self._client.post(self._api_path(), json=params.api_data)
        return TrackingOptOutResponse(**response).data

    def delete(self, tracking_opt_out_id: str) -> TrackingOptOut:
        """
        Remove an email address from the tracking opt-out list so open and
        click tracking can apply again.
        """
        response = self._client.delete(self._api_path(tracking_opt_out_id))
        return TrackingOptOut(**response)

    @staticmethod
    def _api_path(tracking_opt_out_id: Optional[str] = None) -> str:
        path = "/api/tracking_opt_outs"
        if tracking_opt_out_id is not None:
            return f"{path}/{tracking_opt_out_id}"
        return path
