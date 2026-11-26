from pydantic.dataclasses import dataclass

from mailtrap.models.common import RequestParams


@dataclass
class CompanyInfo:
    info_level: str | None = None
    name: str | None = None
    address: str | None = None
    city: str | None = None
    country: str | None = None
    phone: str | None = None
    zip_code: str | None = None
    privacy_policy_url: str | None = None
    terms_of_service_url: str | None = None
    website_url: str | None = None


@dataclass
class CompanyInfoResponse:
    data: CompanyInfo


@dataclass
class CreateCompanyInfoParams(RequestParams):
    name: str
    address: str
    city: str
    country: str
    zip_code: str
    website_url: str
    phone: str | None = None
    privacy_policy_url: str | None = None
    terms_of_service_url: str | None = None
    info_level: str | None = None


@dataclass
class UpdateCompanyInfoParams(RequestParams):
    name: str | None = None
    address: str | None = None
    city: str | None = None
    country: str | None = None
    phone: str | None = None
    zip_code: str | None = None
    privacy_policy_url: str | None = None
    terms_of_service_url: str | None = None
    website_url: str | None = None
    info_level: str | None = None
