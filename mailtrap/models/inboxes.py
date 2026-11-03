"""
Deprecated aliases of the models in `mailtrap.models.sandboxes`.

.. deprecated::
    `Inbox`, `CreateInboxParams` and `UpdateInboxParams` will be removed in a future
    major release; use `Sandbox`, `CreateSandboxParams` and `UpdateSandboxParams`
    from `mailtrap.models.sandboxes` instead.
"""

from mailtrap.models.sandboxes import CreateSandboxParams
from mailtrap.models.sandboxes import Sandbox
from mailtrap.models.sandboxes import UpdateSandboxParams

Inbox = Sandbox
CreateInboxParams = CreateSandboxParams
UpdateInboxParams = UpdateSandboxParams
