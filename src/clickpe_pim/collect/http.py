from __future__ import annotations

import ipaddress
import re
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urljoin, urlsplit

import requests

from clickpe_pim.settings import Settings


@dataclass(frozen=True)
class FetchResult:
    url: str
    final_url: str
    status: str
    http_status: int | None
    body: bytes | None
    media_type: str | None
    error_code: str | None
    retrieved_at: datetime


def _allowed(url: str, hosts: set[str]) -> bool:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.username or parsed.password or not parsed.hostname:
        return False
    host = parsed.hostname.casefold()
    if host not in {h.casefold() for h in hosts}:
        return False
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return True
    return not (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved)


def _challenge(body: bytes) -> bool:
    sample = body[:100_000].decode("utf-8", errors="ignore")
    return bool(re.search(r"captcha|verify you are human|cloudflare challenge|access denied", sample, re.I))


class HttpCollector:
    def __init__(self, settings: Settings, session: requests.Session | None = None, sleep: Callable[[float], None] = time.sleep):
        self.settings = settings
        self.session = session or requests.Session()
        self.sleep = sleep
        self._last_request: dict[str, float] = {}

    def _pace(self, host: str) -> None:
        now = time.monotonic()
        delay = self.settings.scraping.request_delay - (now - self._last_request.get(host, -10**9))
        if delay > 0:
            self.sleep(delay)
        self._last_request[host] = time.monotonic()

    def fetch(self, url: str, *, allowed_hosts: set[str], validators: dict[str, str] | None = None) -> FetchResult:
        stamp = datetime.now(timezone.utc)
        if not _allowed(url, allowed_hosts):
            return FetchResult(url, url, "blocked", None, None, None, "url_not_allowed", stamp)
        headers = {"User-Agent": self.settings.scraping.user_agent, **(validators or {})}
        current = url
        attempts = self.settings.scraping.max_retries + 1
        for attempt in range(attempts):
            try:
                for _redirect in range(6):
                    parsed = urlsplit(current)
                    self._pace(parsed.hostname or "")
                    response = self.session.get(
                        current, headers=headers, timeout=(self.settings.scraping.connect_timeout, self.settings.scraping.read_timeout),
                        stream=True, allow_redirects=False,
                    )
                    stamp = datetime.now(timezone.utc)
                    if response.status_code in {301, 302, 303, 307, 308}:
                        target = urljoin(current, response.headers.get("Location", ""))
                        response.close()
                        if not _allowed(target, allowed_hosts):
                            return FetchResult(url, current, "blocked", response.status_code, None, None, "redirect_not_allowed", stamp)
                        current = target
                        continue
                    break
                else:
                    return FetchResult(url, current, "failed", None, None, None, "too_many_redirects", stamp)
                code = response.status_code
                media_type = response.headers.get("Content-Type", "").split(";", 1)[0] or None
                if code == 304:
                    response.close()
                    if validators and validators.get("X-Previous-SHA256"):
                        return FetchResult(url, current, "not_modified", code, None, media_type, None, stamp)
                    headers = {"User-Agent": self.settings.scraping.user_agent}
                    if attempt + 1 < attempts:
                        continue
                    return FetchResult(url, current, "failed", code, None, media_type, "orphan_304", stamp)
                if code in {404, 410}:
                    response.close()
                    return FetchResult(url, current, "not_found", code, None, media_type, "not_found", stamp)
                if code in {401, 403}:
                    response.close()
                    return FetchResult(url, current, "blocked", code, None, media_type, "access_denied", stamp)
                if code == 429:
                    response.close()
                    retry = response.headers.get("Retry-After")
                    try:
                        wait = min(60, max(0, int(retry or "0")))
                    except ValueError:
                        wait = 0
                    if wait:
                        self.sleep(wait)
                    return FetchResult(url, current, "blocked", code, None, media_type, "rate_limited", stamp)
                if code in {502, 503, 504}:
                    response.close()
                    if attempt + 1 < attempts:
                        self.sleep(2 ** (attempt + 1))
                        continue
                    return FetchResult(url, current, "failed", code, None, media_type, "server_error", stamp)
                if code < 200 or code >= 300:
                    response.close()
                    return FetchResult(url, current, "failed", code, None, media_type, "http_error", stamp)
                chunks: list[bytes] = []
                size = 0
                for chunk in response.iter_content(65_536):
                    if not chunk:
                        continue
                    size += len(chunk)
                    if size > self.settings.scraping.max_bytes:
                        response.close()
                        return FetchResult(url, current, "failed", code, None, media_type, "too_large", stamp)
                    chunks.append(chunk)
                response.close()
                body = b"".join(chunks)
                if _challenge(body):
                    return FetchResult(url, current, "blocked", code, None, media_type, "challenge_page", stamp)
                return FetchResult(url, current, "ok", code, body, media_type, None, stamp)
            except (requests.Timeout, requests.ConnectionError, TimeoutError, OSError):
                if attempt + 1 < attempts:
                    self.sleep(2 ** (attempt + 1))
                    continue
                return FetchResult(url, current, "failed", None, None, None, "network_error", datetime.now(timezone.utc))
        return FetchResult(url, current, "failed", None, None, None, "retry_exhausted", stamp)

