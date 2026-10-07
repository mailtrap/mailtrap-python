import os
from typing import Optional

import mailtrap as mt
from mailtrap.models.common import DeletedObject
from mailtrap.models.paginated_templates import Template
from mailtrap.models.paginated_templates import TemplateListResponse

API_KEY = os.environ["MAILTRAP_API_KEY"]
ACCOUNT_ID = os.environ["MAILTRAP_ACCOUNT_ID"]

client = mt.MailtrapClient(token=API_KEY, account_id=ACCOUNT_ID)
templates_api = client.templates_api.templates


def list_templates() -> TemplateListResponse:
    # `token` is the page number (page-token pagination); `per_page` caps at 100.
    response = templates_api.get_list(mt.TemplateListParams(per_page=50, token=1))
    print(response.data)
    print(response.pagination)
    return response


def create_template(
    name: str,
    subject: str,
    category: str,
    body_html: Optional[str] = None,
    body_text: Optional[str] = None,
) -> Template:
    params = mt.CreateTemplateParams(
        name=name,
        subject=subject,
        category=category,
        body_html=body_html,
        body_text=body_text,
    )
    return templates_api.create(params)


def get_template(template_id: int) -> Template:
    return templates_api.get_by_id(template_id)


def update_template(
    template_id: int,
    name: Optional[str] = None,
    subject: Optional[str] = None,
    category: Optional[str] = None,
    body_html: Optional[str] = None,
    body_text: Optional[str] = None,
) -> Template:
    params = mt.UpdateTemplateParams(
        name=name,
        subject=subject,
        category=category,
        body_html=body_html,
        body_text=body_text,
    )
    return templates_api.update(template_id, params)


def delete_template(template_id: int) -> DeletedObject:
    return templates_api.delete(template_id)


if __name__ == "__main__":
    list_templates()

    created = create_template(
        name="Welcome",
        subject="Welcome aboard",
        category="Onboarding",
        body_html="<h1>Hello!</h1>",
    )
    print(created)

    print(get_template(created.id))
    print(update_template(created.id, subject="Welcome to Mailtrap"))
    print(delete_template(created.id))
