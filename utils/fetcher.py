"""Safe HTTP fetcher used by all collectors.

Design goals (this is a *validation prototype*, not a production crawler):
  - Be polite: realistic UA, timeouts, per-domain throttle, limited retries.
  - Respect boundaries: never bypass login, captcha, paywalls or anti-crawling.
  - Two modes:
      * "existence"  -> light check (HEAD, GET fallback). Used for high-risk /
                        commercial sources where we only confirm a page exists.
      * "fetch"      -> normal GET that returns body text for parsing.
  - Optional Playwright fallback, only triggered when a source declares
    `needs_playwright` AND the plain request failed. Degrades gracefully if
    Playwright is not installed (the caller records needs_playwright instead).
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field

import requests

from .logger import get_logger
from .url_tools import domain_of

logger = get_logger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36 "
        "ListedCompanyDataCollector/validation-prototype"
    ),
    "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


@dataclass
class FetchResult:
    """Normalized result returned for every fetch attempt."""

    ok: bool = False
    status_code: int | None = None
    content_type: str = ""
    final_url: str = ""
    text: str = ""
    content: bytes = b""
    error: str = ""
    used_playwright: bool = False
    elapsed_ms: int = 0


class Fetcher:
    def __init__(
        self,
        timeout: float = 15.0,
        max_retries: int = 1,
        throttle_seconds: float = 1.0,
        max_text_chars: int = 400_000,
        enable_playwright: bool = False,
    ) -> None:
        self.timeout = timeout
        self.max_retries = max_retries
        self.throttle_seconds = throttle_seconds
        self.max_text_chars = max_text_chars
        self.enable_playwright = enable_playwright
        self._session = requests.Session()
        self._session.headers.update(DEFAULT_HEADERS)
        self._last_request: dict[str, float] = {}
        self._lock = threading.Lock()

    # -- throttle -----------------------------------------------------------
    def _respect_throttle(self, url: str) -> None:
        host = domain_of(url)
        with self._lock:
            last = self._last_request.get(host, 0.0)
            wait = self.throttle_seconds - (time.monotonic() - last)
            if wait > 0:
                time.sleep(wait)
            self._last_request[host] = time.monotonic()

    # -- public API ---------------------------------------------------------
    def fetch(self, url: str, mode: str = "fetch", needs_playwright: bool = False) -> FetchResult:
        """Fetch `url`. `mode` is "fetch" or "existence"."""
        if not url:
            return FetchResult(ok=False, error="empty_url")

        result = self._requests_attempt(url, mode)

        if not result.ok and needs_playwright and self.enable_playwright:
            pw = self._playwright_attempt(url)
            if pw is not None:
                return pw
        return result

    # -- requests path ------------------------------------------------------
    def _requests_attempt(self, url: str, mode: str) -> FetchResult:
        last_error = ""
        for attempt in range(self.max_retries + 1):
            self._respect_throttle(url)
            start = time.monotonic()
            try:
                if mode == "existence":
                    resp = self._session.head(url, timeout=self.timeout, allow_redirects=True)
                    # Some servers don't support HEAD; retry with a light GET.
                    if resp.status_code in (403, 404, 405, 501):
                        resp = self._session.get(
                            url, timeout=self.timeout, allow_redirects=True, stream=True
                        )
                        resp.close()
                else:
                    resp = self._session.get(url, timeout=self.timeout, allow_redirects=True)

                elapsed = int((time.monotonic() - start) * 1000)
                content_type = resp.headers.get("Content-Type", "")
                text = ""
                content = b""
                if mode != "existence":
                    if "pdf" in content_type.lower() or url.lower().endswith(".pdf"):
                        content = resp.content
                    else:
                        # requests defaults encoding to ISO-8859-1 when the HTTP
                        # header carries no charset, which mangles GBK/GB2312
                        # Chinese pages. When the header lacks a charset, trust
                        # chardet's detection (apparent_encoding) instead.
                        if "charset=" not in content_type.lower():
                            detected = resp.apparent_encoding
                            if detected:
                                resp.encoding = detected
                        text = (resp.text or "")[: self.max_text_chars]
                return FetchResult(
                    ok=resp.status_code < 400,
                    status_code=resp.status_code,
                    content_type=content_type,
                    final_url=str(resp.url),
                    text=text,
                    content=content,
                    error="" if resp.status_code < 400 else f"http_{resp.status_code}",
                    elapsed_ms=elapsed,
                )
            except requests.exceptions.SSLError as exc:
                last_error = f"ssl_error: {exc}"
            except requests.exceptions.ConnectTimeout:
                last_error = "connect_timeout"
            except requests.exceptions.ReadTimeout:
                last_error = "read_timeout"
            except requests.exceptions.ConnectionError as exc:
                last_error = f"connection_error: {type(exc).__name__}"
            except requests.exceptions.RequestException as exc:
                last_error = f"request_error: {type(exc).__name__}"
            if attempt < self.max_retries:
                time.sleep(self.throttle_seconds)
        logger.info("fetch failed url=%s mode=%s error=%s", url, mode, last_error)
        return FetchResult(ok=False, error=last_error or "unknown_error")

    # -- optional playwright path ------------------------------------------
    def _playwright_attempt(self, url: str) -> FetchResult | None:
        try:
            from playwright.sync_api import sync_playwright  # type: ignore
        except Exception:
            logger.info("playwright requested but not installed url=%s", url)
            return None
        try:
            start = time.monotonic()
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(user_agent=DEFAULT_HEADERS["User-Agent"])
                resp = page.goto(url, timeout=int(self.timeout * 1000), wait_until="domcontentloaded")
                status = resp.status if resp else None
                content_type = ""
                if resp:
                    content_type = resp.headers.get("content-type", "")
                text = (page.content() or "")[: self.max_text_chars]
                browser.close()
            return FetchResult(
                ok=bool(status and status < 400),
                status_code=status,
                content_type=content_type or "text/html",
                final_url=url,
                text=text,
                used_playwright=True,
                elapsed_ms=int((time.monotonic() - start) * 1000),
            )
        except Exception as exc:  # noqa: BLE001 - report any browser error as failure
            logger.info("playwright failed url=%s error=%s", url, exc)
            return FetchResult(ok=False, error=f"playwright_error: {type(exc).__name__}", used_playwright=True)
