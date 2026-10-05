from typing import Optional

from mailtrap.http import HttpClient
from mailtrap.models.account_templates import CreateTemplateParams
from mailtrap.models.account_templates import Template
from mailtrap.models.account_templates import TemplateListParams
from mailtrap.models.account_templates import TemplateListResponse
from mailtrap.models.account_templates import TemplateResponse
from mailtrap.models.account_templates import UpdateTemplateParams
from mailtrap.models.common import DeletedObject


class AccountTemplatesApi:
    def __init__(self, client: HttpClient, account_id: str) -> None:
        self._account_id = account_id
        self._client = client

    def get_list(
        self, params: Optional[TemplateListParams] = None
    ) -> TemplateListResponse:
        """
        List email templates in the account. ``params`` paginates the result;
        omit it for the first page with API defaults.
        """
        query_params = params.api_query_params if params else None
        response = self._client.get(self._api_path(), params=query_params or None)
        return TemplateListResponse(**response)

    def get_by_id(self, template_id: int) -> Template:
        """Get an email template by ID."""
        response = self._client.get(self._api_path(template_id))
        return TemplateResponse(**response).data

    def create(self, template_params: CreateTemplateParams) -> Template:
        """Create a new email template."""
        response = self._client.post(self._api_path(), json=template_params.api_data)
        return TemplateResponse(**response).data

    def update(
        self, template_id: int, template_params: UpdateTemplateParams
    ) -> Template:
        """Update an email template. Only the supplied fields are changed."""
        response = self._client.patch(
            self._api_path(template_id), json=template_params.api_data
        )
        return TemplateResponse(**response).data

    def delete(self, template_id: int) -> DeletedObject:
        """Delete an email template."""
        self._client.delete(self._api_path(template_id))
        return DeletedObject(template_id)

    def _api_path(self, template_id: Optional[int] = None) -> str:
        path = f"/api/accounts/{self._account_id}/templates"
        if template_id is not None:
            return f"{path}/{template_id}"
        return path
