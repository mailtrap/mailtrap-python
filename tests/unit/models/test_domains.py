from mailtrap.models.domains import CreateDomainParams
from mailtrap.models.domains import Domain
from mailtrap.models.domains import SendSetupInstructionsParams


def _domain_dict() -> dict:
    return {
        "id": 1,
        "domain_name": "example.com",
        "demo": False,
        "compliance_status": "verified",
        "dns_verified": True,
        "open_tracking_enabled": True,
        "click_tracking_enabled": True,
        "auto_unsubscribe_link_enabled": False,
        "custom_domain_tracking_enabled": False,
        "health_alerts_enabled": True,
        "critical_alerts_enabled": True,
        "permissions": {
            "can_read": True,
            "can_update": True,
            "can_destroy": True,
        },
    }


class TestDomain:
    def test_parses_inbound_flags_when_present(self) -> None:
        data = {
            **_domain_dict(),
            "inbound_enabled": True,
            "inbound_verified": False,
        }
        domain = Domain(**data)
        assert domain.inbound_enabled is True
        assert domain.inbound_verified is False

    def test_inbound_flags_default_when_absent(self) -> None:
        domain = Domain(**_domain_dict())
        assert domain.inbound_enabled is None
        assert domain.inbound_verified is None


class TestCreateDomainParams:
    def test_api_data_should_return_dict_with_all_props(self) -> None:
        entity = CreateDomainParams(domain_name="test.co")
        assert entity.api_data == {"domain_name": "test.co"}


class TestSendSetupInstructionsParams:
    def test_api_data_should_return_dict_with_all_props(self) -> None:
        entity = SendSetupInstructionsParams(email="example@mail.com")
        assert entity.api_data == {"email": "example@mail.com"}
