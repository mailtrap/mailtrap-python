from datetime import datetime
from typing import Any
from typing import Optional
from typing import Union

from pydantic import Field
from pydantic.dataclasses import dataclass

from mailtrap.models.common import RequestParams


@dataclass
class BlacklistsReport:
    name: str
    url: str
    in_black_list: bool


@dataclass
class Blacklists:
    result: str
    domain: str
    ip: str
    report: list[BlacklistsReport]


@dataclass
class SmtpData:
    mail_from_addr: str
    client_ip: str


@dataclass
class SmtpInformation:
    ok: bool
    data: Optional[SmtpData] = None


@dataclass
class EmailMessage:
    id: int
    inbox_id: int
    subject: str
    sent_at: datetime
    from_email: str
    from_name: str
    to_email: str
    to_name: str
    email_size: int
    is_read: bool
    created_at: datetime
    updated_at: datetime
    html_body_size: int
    text_body_size: int
    human_size: str
    html_path: str
    txt_path: str
    raw_path: str
    download_path: str
    html_source_path: str
    blacklists_report_info: Union[bool, Blacklists]
    smtp_information: SmtpInformation


@dataclass
class UpdateEmailMessageParams(RequestParams):
    is_read: bool

    @property
    def api_data(self) -> dict[str, Any]:
        data = dict(super().api_data)
        data["is_read"] = str(data["is_read"]).lower()
        return data


@dataclass
class ForwardedMessage:
    message: str


@dataclass
class SpamDetail:
    pts: float = Field(alias="Pts")
    rule_name: str = Field(alias="RuleName")
    description: str = Field(alias="Description")


@dataclass
class SpamReport:
    response_code: int = Field(alias="ResponseCode")
    response_message: str = Field(alias="ResponseMessage")
    response_version: str = Field(alias="ResponseVersion")
    score: float = Field(alias="Score")
    spam: bool = Field(alias="Spam")
    threshold: int = Field(alias="Threshold")
    details: list[SpamDetail] = Field(alias="Details")


@dataclass
class EmailClients:
    desktop: list[str]
    mobile: list[str]
    web: list[str]


@dataclass
class ErrorItem:
    error_line: int
    rule_name: str
    email_clients: EmailClients


@dataclass
class AnalysisReport:
    status: str


@dataclass
class AnalysisReportError(AnalysisReport):
    msg: str


@dataclass
class AnalysisReportSuccess(AnalysisReport):
    errors: list[ErrorItem]


@dataclass
class AnalysisReportResponse:
    report: Union[AnalysisReportError, AnalysisReportSuccess]
