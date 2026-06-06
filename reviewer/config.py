import os

# Model used for all AI calls
MODEL = os.getenv("REVIEWER_MODEL", "claude-haiku-4-5-20251001")

# Temperature (0.0 = deterministic, 1.0 = default)
_temperature_raw = os.getenv("REVIEWER_TEMPERATURE")
TEMPERATURE: float | None = float(_temperature_raw) if _temperature_raw is not None else None

# Max tokens for agent responses
_max_tokens_raw = os.getenv("REVIEWER_MAX_TOKENS")
MAX_TOKENS: int | None = int(_max_tokens_raw) if _max_tokens_raw is not None else None

# Max tokens specifically for triage (cheaper, shorter response)
_triage_max_tokens_raw = os.getenv("REVIEWER_TRIAGE_MAX_TOKENS", "256")
TRIAGE_MAX_TOKENS: int = int(_triage_max_tokens_raw)
