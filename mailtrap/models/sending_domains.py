"""
Deprecated aliases of the models in `mailtrap.models.domains`.

.. deprecated::
    `SendingDomain`, `SendingDomainPermissions`, `CreateSendingDomainParams` and
    `UpdateSendingDomainParams` will be removed in a future major release; use
    `Domain`, `DomainPermissions`, `CreateDomainParams` and `UpdateDomainParams`
    from `mailtrap.models.domains` instead.
"""

from mailtrap.models.domains import CreateDomainParams
from mailtrap.models.domains import DnsRecord
from mailtrap.models.domains import Domain
from mailtrap.models.domains import DomainPermissions
from mailtrap.models.domains import SendSetupInstructionsParams
from mailtrap.models.domains import SendSetupInstructionsResponse
from mailtrap.models.domains import UpdateDomainParams

SendingDomain = Domain
SendingDomainPermissions = DomainPermissions
CreateSendingDomainParams = CreateDomainParams
UpdateSendingDomainParams = UpdateDomainParams

__all__ = [
    "CreateSendingDomainParams",
    "DnsRecord",
    "SendSetupInstructionsParams",
    "SendSetupInstructionsResponse",
    "SendingDomain",
    "SendingDomainPermissions",
    "UpdateSendingDomainParams",
]
