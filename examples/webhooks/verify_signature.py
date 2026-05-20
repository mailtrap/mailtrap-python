import hashlib
import hmac

import mailtrap as mt

# --- Direct verification (e.g. for unit tests or custom routers) ----------
payload = '{"event":"delivery","message_id":"abc-123"}'
signing_secret = "8d9a3c0e7f5b2d4a6c1e9f8b3a7d5c2e"
signature = hmac.new(
    signing_secret.encode("utf-8"),
    payload.encode("utf-8"),
    hashlib.sha256,
).hexdigest()

assert mt.verify_signature(payload, signature, signing_secret) is True

# Bad input never raises — it returns False:
assert mt.verify_signature(payload, "not-hex", signing_secret) is False
assert mt.verify_signature(payload, "", signing_secret) is False
