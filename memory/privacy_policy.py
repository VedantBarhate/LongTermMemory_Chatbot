import re


class PrivacyPolicy:

    VALID_MODES = {"AUTO", "ASK", "DISABLED"}

    VALID_TYPES = {
        "profile",
        "preference",
        "interest",
        "skill",
        "project",
        "goal",
        "habit",
        "other"
    }

    # Obvious credentials and secrets
    SECRET_PATTERNS = [
        re.compile(
            r"\bpassword\s*(?:is|=|:)\s*\S+",
            re.IGNORECASE
        ),
        re.compile(
            r"\b(?:api[_ -]?key|access[_ -]?token|"
            r"secret[_ -]?key)\s*(?:is|=|:)\s*\S+",
            re.IGNORECASE
        ),
        re.compile(
            r"\bsk-[A-Za-z0-9_-]{10,}\b"
        ),
        re.compile(
            r"\bBearer\s+[A-Za-z0-9._~+/-]+=*\b",
            re.IGNORECASE
        ),
        re.compile(
            r"\b\d{13,19}\b"
        )
    ]

    # Sensitive personal information that should not
    # be persisted by this project's default policy.
    SENSITIVE_PATTERNS = [
        re.compile(
            r"\b(?:my|i have|i was diagnosed with|"
            r"i suffer from)\s+(?:diagnosed with\s+)?"
            r"(?:diabetes|HIV|cancer|depression|"
            r"bipolar disorder|schizophrenia)\b",
            re.IGNORECASE
        ),
        re.compile(
            r"\bmy\s+(?:bank account|credit card|"
            r"debit card|passport number|"
            r"government id|social security number)\b",
            re.IGNORECASE
        )
    ]

    def __init__(self, mode="AUTO"):

        self.set_mode(mode)

    def set_mode(self, mode):

        mode = mode.upper()

        if mode not in self.VALID_MODES:
            raise ValueError(
                f"Invalid mode: {mode}. "
                f"Choose from {self.VALID_MODES}."
            )

        self.mode = mode

    def _validate_candidate(self, candidate):

        if not isinstance(candidate, dict):
            return False

        text = candidate.get("text")
        memory_type = candidate.get("type")
        importance = candidate.get("importance")
        confidence = candidate.get("confidence")

        if not isinstance(text, str) or not text.strip():
            return False

        if len(text) > 1000:
            return False

        if memory_type not in self.VALID_TYPES:
            return False

        # Reject booleans as numeric scores too.
        if (
            isinstance(importance, bool)
            or not isinstance(importance, (int, float))
            or not 0 <= importance <= 1
        ):
            return False

        if (
            isinstance(confidence, bool)
            or not isinstance(confidence, (int, float))
            or not 0 <= confidence <= 1
        ):
            return False

        return True

    def _check_sensitivity(self, text):

        for pattern in self.SECRET_PATTERNS:
            if pattern.search(text):
                return "credential_or_secret"

        for pattern in self.SENSITIVE_PATTERNS:
            if pattern.search(text):
                return "sensitive_personal_information"

        return None

    def approve_candidate(self, candidate):

        # Validate structure before processing.
        if not self._validate_candidate(candidate):
            return False, "invalid_candidate"

        # DISABLED means no new long-term memories.
        if self.mode == "DISABLED":
            return False, "memory_disabled"

        text = candidate["text"]

        # Never ask for consent to store a detected secret.
        reason = self._check_sensitivity(text)

        if reason:
            return False, reason

        # Require explicit approval in ASK mode.
        if self.mode == "ASK":

            print("\nMemory candidate:")
            print(f"  Text: {text}")
            print(f"  Type: {candidate['type']}")

            answer = input(
                "Store this memory? (y/n): "
            ).strip().lower()

            if answer not in {"y", "yes"}:
                return False, "user_declined"

        return True, "approved"

    def filter_candidates(self, candidates):

        approved = []
        rejected = []

        for candidate in candidates:

            is_approved, reason = (
                self.approve_candidate(candidate)
            )

            if is_approved:
                approved.append(candidate)
            else:
                rejected.append({
                    "candidate": candidate,
                    "reason": reason
                })

        return {
            "approved": approved,
            "rejected": rejected
        }