import hashlib
import hmac

from mailtrap.webhooks import SIGNATURE_HEX_LENGTH
from mailtrap.webhooks import verify_signature

# ---------------------------------------------------------------------------
# Cross-SDK fixture
#
# The (payload, signing_secret, expected_signature) triple below is the
# canonical fixture shared verbatim by every official Mailtrap SDK
# (mailtrap-ruby, mailtrap-python, mailtrap-php, mailtrap-nodejs,
# mailtrap-java, mailtrap-dotnet). Any change here MUST be mirrored in the
# equivalent test files in the other SDKs so the helpers stay byte-for-byte
# compatible across languages.
# ---------------------------------------------------------------------------
FIXTURE_PAYLOAD = (
    '{"event":"delivery","sending_stream":"transactional","category":"welcome",'
    '"message_id":"a8b1d8f6-1f8d-4a3c-9b2e-1a2b3c4d5e6f",'
    '"email":"recipient@example.com",'
    '"event_id":"f1e2d3c4-b5a6-7890-1234-567890abcdef",'
    '"timestamp":1716070000}'
)
FIXTURE_SIGNING_SECRET = "8d9a3c0e7f5b2d4a6c1e9f8b3a7d5c2e"
FIXTURE_EXPECTED_SIGNATURE = (
    "6d262e2611cd09be1f948382b5c611d63b0e585c4c9c5e40139d6ac3876d5433"
)


class TestVerifySignature:
    # --- 1. Valid signature for given payload + secret ----------------------
    def test_returns_true_for_valid_signature_payload_and_secret(self) -> None:
        assert (
            verify_signature(
                FIXTURE_PAYLOAD,
                FIXTURE_EXPECTED_SIGNATURE,
                FIXTURE_SIGNING_SECRET,
            )
            is True
        )

    # --- 2. Wrong secret ----------------------------------------------------
    def test_returns_false_with_wrong_signing_secret(self) -> None:
        assert (
            verify_signature(
                FIXTURE_PAYLOAD,
                FIXTURE_EXPECTED_SIGNATURE,
                "ffffffffffffffffffffffffffffffff",
            )
            is False
        )

    # --- 3. Payload tampered (one byte changed) -----------------------------
    def test_returns_false_when_payload_is_tampered(self) -> None:
        tampered = FIXTURE_PAYLOAD.replace("delivery", "Delivery")

        assert (
            verify_signature(
                tampered,
                FIXTURE_EXPECTED_SIGNATURE,
                FIXTURE_SIGNING_SECRET,
            )
            is False
        )

    # --- 4. Signature with wrong length -------------------------------------
    def test_returns_false_without_raising_when_signature_too_short(self) -> None:
        too_short = FIXTURE_EXPECTED_SIGNATURE[:31]

        assert (
            verify_signature(FIXTURE_PAYLOAD, too_short, FIXTURE_SIGNING_SECRET) is False
        )

    # --- 5. Signature with non-hex characters -------------------------------
    def test_returns_false_without_raising_for_non_hex_signature(self) -> None:
        not_hex = "z" * SIGNATURE_HEX_LENGTH

        assert verify_signature(FIXTURE_PAYLOAD, not_hex, FIXTURE_SIGNING_SECRET) is False

    # --- 6. Empty signature string ------------------------------------------
    def test_returns_false_for_empty_signature(self) -> None:
        assert verify_signature(FIXTURE_PAYLOAD, "", FIXTURE_SIGNING_SECRET) is False

    # --- 7. Empty signing_secret --------------------------------------------
    def test_returns_false_for_empty_signing_secret(self) -> None:
        assert verify_signature(FIXTURE_PAYLOAD, FIXTURE_EXPECTED_SIGNATURE, "") is False

    # --- 8. Empty payload + non-empty signature -----------------------------
    def test_returns_false_for_empty_payload(self) -> None:
        assert (
            verify_signature("", FIXTURE_EXPECTED_SIGNATURE, FIXTURE_SIGNING_SECRET)
            is False
        )

    # --- 9. Known-good cross-SDK fixture ------------------------------------
    def test_matches_hardcoded_hmac_sha256_digest_for_shared_fixture(self) -> None:
        # Recompute the digest in-place so a regression in the stdlib or the
        # fixture itself fails loudly: this is the byte-for-byte contract
        # every other Mailtrap SDK must satisfy.
        computed = hmac.new(
            FIXTURE_SIGNING_SECRET.encode("utf-8"),
            FIXTURE_PAYLOAD.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        assert computed == FIXTURE_EXPECTED_SIGNATURE
        assert (
            verify_signature(
                FIXTURE_PAYLOAD,
                FIXTURE_EXPECTED_SIGNATURE,
                FIXTURE_SIGNING_SECRET,
            )
            is True
        )

    # --- Bonus: accepts bytes payload ---------------------------------------
    def test_accepts_bytes_payload(self) -> None:
        assert (
            verify_signature(
                FIXTURE_PAYLOAD.encode("utf-8"),
                FIXTURE_EXPECTED_SIGNATURE,
                FIXTURE_SIGNING_SECRET,
            )
            is True
        )
