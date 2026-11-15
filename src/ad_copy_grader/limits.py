"""In-memory rate limiting and daily request cap.

In-memory rate limiting is deterministic and safe only when deployed with
max-instances=1 on Cloud Run.
"""

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Literal

from ad_copy_grader.models import Language

LimitReason = Literal["ip_rate_limit", "daily_cap"]

LIMIT_MESSAGES: dict[LimitReason, dict[Language, str]] = {
    "ip_rate_limit": {
        "en": (
            "Rate limit exceeded: maximum {limit} requests per minute per IP. "
            "Please wait a moment and try again."
        ),
        "pt": (
            "Limite de requisições por minuto excedido: máximo de {limit} por IP. "
            "Aguarde um instante e tente novamente."
        ),
    },
    "daily_cap": {
        "en": (
            "Daily public demo quota ({cap} requests/day) reached. "
            "Please explore the pre-evaluated scenarios or try again tomorrow (UTC)."
        ),
        "pt": (
            "A cota diária da demonstração pública ({cap} requisições/dia) foi atingida. "
            "Explore os cenários pré-avaliados ou tente novamente amanhã (UTC)."
        ),
    },
}


class RateLimiter:
    """In-memory sliding window rate limiter and daily request cap.

    In-memory rate limiting is deterministic and safe only when deployed with
    max-instances=1 on Cloud Run.
    """

    def __init__(
        self,
        rate_limit_per_minute: int = 5,
        daily_request_cap: int = 200,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        """Initialize the rate limiter.

        In-memory rate limiting is deterministic and safe only when deployed with
        max-instances=1 on Cloud Run.
        """
        self.rate_limit_per_minute = rate_limit_per_minute
        self.daily_request_cap = daily_request_cap
        self._clock: Callable[[], datetime] = (
            clock if clock is not None else lambda: datetime.now(UTC)
        )
        self.daily_count: int = 0
        self._current_date = self._clock().date()
        self._ip_history: dict[str, list[datetime]] = {}

    def check_and_record(
        self, client_ip: str, lang: Language = "en"
    ) -> tuple[bool, LimitReason | None, str | None]:
        """Check rate limits and record request timestamp if allowed."""
        now = self._clock()
        today = now.date()

        if today > self._current_date:
            self._current_date = today
            self.daily_count = 0
            self._ip_history.clear()

        cutoff = now - timedelta(seconds=60)
        current_timestamps = [ts for ts in self._ip_history.get(client_ip, []) if ts >= cutoff]

        if len(current_timestamps) >= self.rate_limit_per_minute:
            self._ip_history[client_ip] = current_timestamps
            message = LIMIT_MESSAGES["ip_rate_limit"][lang].format(limit=self.rate_limit_per_minute)
            return (False, "ip_rate_limit", message)

        if self.daily_count >= self.daily_request_cap:
            self._ip_history[client_ip] = current_timestamps
            message = LIMIT_MESSAGES["daily_cap"][lang].format(cap=self.daily_request_cap)
            return (False, "daily_cap", message)

        current_timestamps.append(now)
        self._ip_history[client_ip] = current_timestamps
        self.daily_count += 1
        return (True, None, None)


def extract_client_ip(x_forwarded_for: str | None, fallback_host: str | None) -> str:
    """Extract the client IP appended by Cloud Run's Google Front End, or the fallback host.

    The GFE appends the real client IP as the LAST X-Forwarded-For entry; anything before it
    is client-supplied and forgeable (verified on 2026-11-15: no header -> 1 entry, forged
    header -> 2 entries). Using the first entry would let a client bypass the per-IP limit.
    """
    if x_forwarded_for:
        entries = [part.strip() for part in x_forwarded_for.split(",") if part.strip()]
        if entries:
            return entries[-1]
    return fallback_host or "unknown"


def count_forwarded_hops(x_forwarded_for: str | None) -> int:
    """Count non-empty X-Forwarded-For entries (logged to verify the proxy chain, never the IPs)."""
    if not x_forwarded_for:
        return 0
    return sum(1 for part in x_forwarded_for.split(",") if part.strip())


__all__ = [
    "LIMIT_MESSAGES",
    "LimitReason",
    "RateLimiter",
    "count_forwarded_hops",
    "extract_client_ip",
]
