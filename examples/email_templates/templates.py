import os

import mailtrap as mt
from mailtrap.models.common import DeletedObject
from mailtrap.models.templates import EmailTemplate

API_KEY = os.environ["MAILTRAP_API_KEY"]
ACCOUNT_ID = os.environ["MAILTRAP_ACCOUNT_ID"]

client = mt.MailtrapClient(token=API_KEY, account_id=ACCOUNT_ID)
templates_api = client.email_templates_api.templates


def list_templates() -> list[EmailTemplate]:
    return templates_api.get_list()


def create_template(
    name: str,
    subject: str,
    category: str,
    body_text: str | None = None,
    body_html: str | None = None,
) -> EmailTemplate:
    params = mt.CreateEmailTemplateParams(
        name=name,
        subject=subject,
        category=category,
        body_text=body_text,
        body_html=body_html,
    )
    return templates_api.create(params)


def get_template(template_id: int) -> EmailTemplate:
    return templates_api.get_by_id(template_id)


def update_template(
    template_id: int,
    name: str | None = None,
    subject: str | None = None,
    category: str | None = None,
    body_text: str | None = None,
    body_html: str | None = None,
) -> EmailTemplate:
    params = mt.UpdateEmailTemplateParams(
        name=name,
        subject=subject,
        category=category,
        body_text=body_text,
        body_html=body_html,
    )
    return templates_api.update(template_id, params)


def delete_template(template_id: int) -> DeletedObject:
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

    template = get_template(template_id=created.id)
    print(template)

    updated = update_template(
        template_id=created.id,
        name=f"{template.name}-updated",
        subject=f"{template.subject}-updated",
        body_text=f"{template.body_text}\nUpdated content.",
    )
    print(updated)

    deleted = delete_template(template_id=created.id)
    print(deleted)
