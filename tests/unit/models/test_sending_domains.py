from mailtrap.models.sending_domains import CreateSendingDomainParams
from mailtrap.models.sending_domains import SendSetupInstructionsParams


class TestCreateSendingDomainParams:
    def test_api_data_should_return_dict_with_all_props(self) -> None:
        entity = CreateSendingDomainParams(domain_name="test.co")
        assert entity.api_data == {"domain_name": "test.co"}


class TestSendSetupInstructionsParams:
    def test_api_data_should_return_dict_with_all_props(self) -> None:
        entity = SendSetupInstructionsParams(email="example@mail.com")
        assert entity.api_data == {"email": "example@mail.com"}
