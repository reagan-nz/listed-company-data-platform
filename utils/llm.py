"""Optional LLM interface.

Policy (from the spec): the LLM is used ONLY for
  - summary
  - classification
  - event extraction
  - evidence-sentence extraction
and only over text that was already fetched from a public source.

It is disabled by default. When disabled, the methods fall back to simple,
deterministic heuristics so the framework runs with no API key. Wiring a real
provider is intentionally left as a single `_call_provider` hook.
"""

from __future__ import annotations

from .logger import get_logger
from .text_cleaner import first_sentence, truncate

logger = get_logger(__name__)


class LLMClient:
    def __init__(self, enabled: bool = False, provider: str = "") -> None:
        self.enabled = enabled
        self.provider = provider
        if enabled and not provider:
            logger.info("LLM enabled but no provider configured; using heuristic fallback.")

    # -- public capabilities -----------------------------------------------
    def summarize(self, text: str, max_len: int = 200) -> str:
        if self.enabled and self.provider:
            return self._call_provider("summarize", text, max_len)
        return truncate(text, max_len)

    def classify(self, text: str, labels: list[str]) -> str:
        if self.enabled and self.provider:
            return self._call_provider("classify", text, labels=labels)
        # Heuristic: first label whose keyword appears in the text.
        for label in labels:
            if label and label in (text or ""):
                return label
        return ""

    def extract_events(self, text: str) -> list[str]:
        if self.enabled and self.provider:
            result = self._call_provider("extract_events", text)
            return result if isinstance(result, list) else []
        return []

    def evidence_sentence(self, text: str, query: str | None = None, max_len: int = 200) -> str:
        if self.enabled and self.provider:
            return self._call_provider("evidence", text, query=query, max_len=max_len)
        # Heuristic: sentence containing the query, else the first sentence.
        if query and text and query in text:
            idx = text.find(query)
            window = text[max(0, idx - 60) : idx + 140]
            return truncate(window, max_len)
        return first_sentence(text, max_len)

    # -- provider hook ------------------------------------------------------
    def _call_provider(self, task: str, text: str, *args, **kwargs):
        """Placeholder for a real provider call.

        Wire your provider here (kept out of the prototype on purpose). Until
        then, behave like the disabled path so runs never break.
        """
        logger.info("LLM provider '%s' not wired; falling back for task=%s", self.provider, task)
        if task == "summarize":
            return truncate(text, args[0] if args else 200)
        if task == "evidence":
            return self.evidence_sentence(text, kwargs.get("query"), kwargs.get("max_len", 200))
        if task == "extract_events":
            return []
        return ""
