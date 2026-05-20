"""Helpers for working with inbound Mailtrap webhooks.

See https://docs.mailtrap.io/email-api-smtp/advanced/webhooks#verifying-the-signature
for the algorithm reference.
"""

import hashlib
import hmac
from typing import Union

# Hex-encoded HMAC-SHA256 signature length (SHA-256 produces 32 bytes / 64 hex chars).
SIGNATURE_HEX_LENGTH = 64


def verify_signature(
    payload: Union[str, bytes],
    signature: str,
    signing_secret: str,
) -> bool:
    """Verify the HMAC-SHA256 signature of a Mailtrap webhook payload.

    Mailtrap signs every outbound webhook by computing
    ``HMAC-SHA256(signing_secret, raw_request_body)`` and sending the
    lowercase hex digest in the ``Mailtrap-Signature`` HTTP header. Compute
    the same digest on your side and compare it in constant time.

    The comparison is performed with :func:`hmac.compare_digest` to avoid
    timing side-channels.

    The function never raises on inputs that could plausibly arrive over the
    wire (empty strings, wrong-length signatures, non-hex characters, missing
    secret) -- it simply returns ``False``. This makes it safe to call
    directly from a request handler without wrapping in ``try``/``except``.

    :param payload: The raw request body, exactly as received. Accepts
        ``str`` (encoded as UTF-8 internally) or ``bytes``. **Do not** parse
        and re-serialize the JSON -- re-encoding may reorder keys or alter
        whitespace and invalidate the signature.
    :param signature: The value of the ``Mailtrap-Signature`` HTTP header
        (lowercase hex string).
    :param signing_secret: The webhook's ``signing_secret``, returned by
        :meth:`mailtrap.api.resources.webhooks.WebhooksApi.create` on
        webhook creation.
    :returns: ``True`` if the signature is valid for the given payload and
        secret, ``False`` otherwise.
    """
    if not isinstance(signature, str) or not signature:
        return False
    if not isinstance(signing_secret, str) or not signing_secret:
        return False
    if not isinstance(payload, (str, bytes)):
        return False
    if len(payload) == 0:
        return False
    if len(signature) != SIGNATURE_HEX_LENGTH:
        return False

    if isinstance(payload, str):
        payload_bytes = payload.encode("utf-8")
    else:
        payload_bytes = payload

    try:
        expected = hmac.new(
            signing_secret.encode("utf-8"),
            payload_bytes,
            hashlib.sha256,
        ).hexdigest()
    except (TypeError, ValueError):
        return False

    return hmac.compare_digest(expected, signature)
