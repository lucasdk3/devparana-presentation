import os

# Model used for all AI calls
MODEL = os.getenv("REVIEWER_MODEL", "claude-haiku-4-5-20251001")

# Max tokens for review responses
MAX_TOKENS: int = int(os.getenv("REVIEWER_MAX_TOKENS", "4096"))

# Max tokens specifically for triage (cheaper, shorter response)
TRIAGE_MAX_TOKENS: int = int(os.getenv("REVIEWER_TRIAGE_MAX_TOKENS", "256"))
