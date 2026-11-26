from mailtrap.http import HttpClient
from mailtrap.models.common import DeletedObject
from mailtrap.models.templates import CreateEmailTemplateParams
from mailtrap.models.templates import EmailTemplate
from mailtrap.models.templates import UpdateEmailTemplateParams


class TemplatesApi:
    def __init__(self, client: HttpClient, account_id: str) -> None:
        self._account_id = account_id
        self._client = client

    def get_list(self) -> list[EmailTemplate]:
        """Get all email templates existing in your account."""
        response = self._client.get(self._api_path())
        return [EmailTemplate(**template) for template in response]

    def get_by_id(self, template_id: int) -> EmailTemplate:
        """Get an email template by ID."""
        response = self._client.get(self._api_path(template_id))
        return EmailTemplate(**response)

    def create(self, template_params: CreateEmailTemplateParams) -> EmailTemplate:
        """Create a new email template."""
        response = self._client.post(
            self._api_path(),
            json={"email_template": template_params.api_data},
        )
        return EmailTemplate(**response)

    def update(
        self, template_id: int, template_params: UpdateEmailTemplateParams
    ) -> EmailTemplate:
        """Update an email template."""
        response = self._client.patch(
            self._api_path(template_id),
            json={"email_template": template_params.api_data},
        )
        return EmailTemplate(**response)

    def delete(self, template_id: int) -> DeletedObject:
        """Delete an email template."""
        self._client.delete(self._api_path(template_id))
        return DeletedObject(template_id)

    def _api_path(self, template_id: int | None = None) -> str:
        path = f"/api/accounts/{self._account_id}/email_templates"
        if template_id:
            return f"{path}/{template_id}"
        return path
