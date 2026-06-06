import os

# Model used for all AI calls
MODEL = os.getenv("REVIEWER_MODEL", "claude-haiku-4-5-20251001")

# Max USD budget per agent call (ClaudeAgentOptions.max_budget_usd)
_max_budget_raw = os.getenv("REVIEWER_MAX_BUDGET_USD")
MAX_BUDGET_USD: float | None = float(_max_budget_raw) if _max_budget_raw else None

# Max tokens specifically for triage (cheaper, shorter response)
_triage_max_tokens_raw = os.getenv("REVIEWER_TRIAGE_MAX_TOKENS", "256")
TRIAGE_MAX_TOKENS: int = int(_triage_max_tokens_raw)
