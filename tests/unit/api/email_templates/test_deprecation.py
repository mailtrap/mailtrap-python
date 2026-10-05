import pytest

from mailtrap.api.templates import EmailTemplatesApi
from mailtrap.config import GENERAL_HOST
from mailtrap.http import HttpClient


def test_templates_should_warn_that_the_group_is_deprecated() -> None:
    api = EmailTemplatesApi(account_id="321", client=HttpClient(GENERAL_HOST))

    with pytest.warns(DeprecationWarning, match="MailtrapClient.templates_api"):
        _ = api.templates
