from typing import Optional

import mailtrap as mt
from mailtrap.models.common import DeletedObject
from mailtrap.models.templates import EmailTemplate

API_TOKEN = "YOUR_API_TOKEN"
ACCOUNT_ID = "YOUR_ACCOUNT_ID"

client = mt.MailtrapClient(token=API_TOKEN, account_id=ACCOUNT_ID)
templates_api = client.email_templates_api.templates


def list_templates() -> list[EmailTemplate]:
    return templates_api.get_list()


def create_template(
    name: str,
    subject: str,
    category: str,
    body_text: Optional[str] = None,
    body_html: Optional[str] = None,
) -> EmailTemplate:
    params = mt.CreateEmailTemplateParams(
        name=name,
        subject=subject,
        category=category,
        body_text=body_text,
        body_html=body_html,
    )
    return templates_api.create(params)


def get_template(template_id: str) -> EmailTemplate:
    return templates_api.get_by_id(template_id)


def update_template(
    template_id: str,
    name: Optional[str] = None,
    subject: Optional[str] = None,
    category: Optional[str] = None,
    body_text: Optional[str] = None,
    body_html: Optional[str] = None,
) -> EmailTemplate:
    params = mt.UpdateEmailTemplateParams(
        name=name,
        subject=subject,
        category=category,
        body_text=body_text,
        body_html=body_html,
    )
    return templates_api.update(template_id, params)


def delete_template(template_id: str) -> DeletedObject:
    return templates_api.delete(template_id)


if __name__ == "__main__":
    created = create_template(
        name="Example Template",
        subject="Hello",
        category="transactional",
        body_text="Hello world",
    )
    print(created)

    templates = list_templates()
    print(templates)

    template_id = templates[0].id
    template = get_template(template_id=template_id)
    print(template)

    updated = update_template(
        template_id=template_id,
        name=f"{template.name}-updated",
        subject=f"{template.subject}-updated",
        body_text=f"{template.body_text}\nUpdated content.",
    )
    print(updated)

    deleted = delete_template(template_id=template_id)
    print(deleted)
