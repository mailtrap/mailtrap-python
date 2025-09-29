from mailtrap.models.mail import Address
from mailtrap.models.mail import Attachment
from mailtrap.models.mail import BatchEmailRequest
from mailtrap.models.mail import BatchMail
from mailtrap.models.mail import BatchMailFromTemplate


class TestBatchMail:
    ADDRESS = Address(email="joe@mail.com")
    ADDRESS_API_DATA = {"email": "joe@mail.com"}

    ATTACHMENT = Attachment(content=b"base64_content", filename="file.txt")
    ATTACHMENT_API_DATA = {"content": "base64_content", "filename": "file.txt"}

    def test_api_data_should_return_dict_with_required_props_only(self) -> None:
        entity = BatchMail(
            sender=self.ADDRESS,
            subject="Email subject",
            text="email text",
        )
        assert entity.api_data == {
            "from": self.ADDRESS_API_DATA,
            "subject": "Email subject",
            "text": "email text",
        }

    def test_api_data_should_return_dict_with_all_props(self) -> None:
        entity = BatchMail(
            sender=self.ADDRESS,
            subject="Email subject",
            text="email text",
            html="email html",
            attachments=[self.ATTACHMENT],
            headers={"key": "value"},
            custom_variables={"var": 42},
            category="test_category",
            reply_to=self.ADDRESS,
        )

        assert entity.api_data == {
            "from": self.ADDRESS_API_DATA,
            "subject": "Email subject",
            "text": "email text",
            "html": "email html",
            "attachments": [self.ATTACHMENT_API_DATA],
            "headers": {"key": "value"},
            "custom_variables": {"var": 42},
            "category": "test_category",
            "reply_to": self.ADDRESS_API_DATA,
        }


class TestBatchMailFromTremplate:
    ADDRESS = Address(email="joe@mail.com")
    ADDRESS_API_DATA = {"email": "joe@mail.com"}

    ATTACHMENT = Attachment(content=b"base64_content", filename="file.txt")
    ATTACHMENT_API_DATA = {"content": "base64_content", "filename": "file.txt"}

    def test_api_data_should_return_dict_with_required_props_only(self) -> None:
        entity = BatchMailFromTemplate(
            sender=self.ADDRESS,
            template_uuid="fake_uuid",
        )
        assert entity.api_data == {
            "from": self.ADDRESS_API_DATA,
            "template_uuid": "fake_uuid",
        }

    def test_api_data_should_return_dict_with_all_props(self) -> None:
        entity = BatchMailFromTemplate(
            sender=self.ADDRESS,
            template_uuid="fake_uuid",
            template_variables={"username": "Joe"},
            attachments=[self.ATTACHMENT],
            headers={"key": "value"},
            custom_variables={"var": 42},
            reply_to=self.ADDRESS,
        )

        assert entity.api_data == {
            "from": self.ADDRESS_API_DATA,
            "template_uuid": "fake_uuid",
            "template_variables": {"username": "Joe"},
            "attachments": [self.ATTACHMENT_API_DATA],
            "headers": {"key": "value"},
            "custom_variables": {"var": 42},
            "reply_to": self.ADDRESS_API_DATA,
        }


class TestBatchEmailRequest:
    ADDRESS = Address(email="joe@mail.com")
    ADDRESS_API_DATA = {"email": "joe@mail.com"}

    ATTACHMENT = Attachment(content=b"base64_content", filename="file.txt")
    ATTACHMENT_API_DATA = {"content": "base64_content", "filename": "file.txt"}

    def test_api_data_should_return_dict_with_required_props_only(self) -> None:
        entity = BatchEmailRequest(
            to=[self.ADDRESS],
        )
        assert entity.api_data == {"to": [self.ADDRESS_API_DATA]}

    def test_api_data_should_return_dict_with_all_props_for_inline_mail(self) -> None:
        entity = BatchEmailRequest(
            sender=self.ADDRESS,
            to=[self.ADDRESS],
            subject="Email subject",
            text="email text",
            html="email html",
            attachments=[self.ATTACHMENT],
            headers={"key": "value"},
            custom_variables={"var": 42},
            category="test_category",
            reply_to=self.ADDRESS,
        )

        assert entity.api_data == {
            "from": self.ADDRESS_API_DATA,
            "to": [self.ADDRESS_API_DATA],
            "subject": "Email subject",
            "text": "email text",
            "html": "email html",
            "attachments": [self.ATTACHMENT_API_DATA],
            "headers": {"key": "value"},
            "custom_variables": {"var": 42},
            "category": "test_category",
            "reply_to": self.ADDRESS_API_DATA,
        }

    def test_api_data_should_return_dict_with_all_props_for_template_mail(self) -> None:
        entity = BatchEmailRequest(
            sender=self.ADDRESS,
            to=[self.ADDRESS],
            attachments=[self.ATTACHMENT],
            headers={"key": "value"},
            custom_variables={"var": 42},
            reply_to=self.ADDRESS,
            template_uuid="fake_uuid",
            template_variables={"username": "Joe"},
        )

        assert entity.api_data == {
            "from": self.ADDRESS_API_DATA,
            "to": [self.ADDRESS_API_DATA],
            "attachments": [self.ATTACHMENT_API_DATA],
            "headers": {"key": "value"},
            "custom_variables": {"var": 42},
            "reply_to": self.ADDRESS_API_DATA,
            "template_uuid": "fake_uuid",
            "template_variables": {"username": "Joe"},
        }
