"""Tests for rate limiting, sliding window expiration, daily cap, and IP extraction."""

from datetime import UTC, datetime, timedelta

from ad_copy_grader.limits import RateLimiter, extract_client_ip


class MockClock:
    """Deterministic clock mock for simulating time progression in tests."""

    def __init__(self, start_time: datetime | None = None) -> None:
        self.current = start_time or datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)

    def __call__(self) -> datetime:
        return self.current

    def advance(self, seconds: float = 0, days: int = 0) -> None:
        self.current += timedelta(seconds=seconds, days=days)


def test_rate_limiter_per_ip_limit_and_messages() -> None:
    """Verify per-IP sliding window allows limit requests and blocks subsequent with i18n."""
    clock = MockClock()
    limiter = RateLimiter(rate_limit_per_minute=5, daily_request_cap=200, clock=clock)

    for _ in range(5):
        allowed, reason, message = limiter.check_and_record("192.168.1.1", lang="en")
        assert allowed is True
        assert reason is None
        assert message is None

    # 6th request from same IP is blocked in English
    allowed_en, reason_en, message_en = limiter.check_and_record("192.168.1.1", lang="en")
    assert allowed_en is False
    assert reason_en == "ip_rate_limit"
    assert message_en == (
        "Rate limit exceeded: maximum 5 requests per minute per IP. "
        "Please wait a moment and try again."
    )

    # 7th request from same IP is blocked in Portuguese
    allowed_pt, reason_pt, message_pt = limiter.check_and_record("192.168.1.1", lang="pt")
    assert allowed_pt is False
    assert reason_pt == "ip_rate_limit"
    assert message_pt == (
        "Limite de requisições por minuto excedido: máximo de 5 por IP. "
        "Aguarde um instante e tente novamente."
    )

    # Blocked requests do not increment the daily count
    assert limiter.daily_count == 5


def test_rate_limiter_sliding_window_expiration() -> None:
    """Verify advancing the clock by 61 seconds allows requests from the IP again."""
    clock = MockClock()
    limiter = RateLimiter(rate_limit_per_minute=5, daily_request_cap=200, clock=clock)

    for _ in range(5):
        allowed, _, _ = limiter.check_and_record("192.168.1.1")
        assert allowed is True

    # 6th request blocked
    allowed_blocked, _, _ = limiter.check_and_record("192.168.1.1")
    assert allowed_blocked is False

    # Advance clock past the 60-second window
    clock.advance(seconds=61)

    allowed_after, reason_after, msg_after = limiter.check_and_record("192.168.1.1")
    assert allowed_after is True
    assert reason_after is None
    assert msg_after is None
    assert limiter.daily_count == 6


def test_rate_limiter_independent_ip_buckets() -> None:
    """Verify different client IPs have independent per-minute buckets."""
    clock = MockClock()
    limiter = RateLimiter(rate_limit_per_minute=5, daily_request_cap=200, clock=clock)

    for _ in range(5):
        allowed, _, _ = limiter.check_and_record("10.0.0.1")
        assert allowed is True

    # IP 10.0.0.1 is now rate limited
    allowed_ip1, reason_ip1, _ = limiter.check_and_record("10.0.0.1")
    assert allowed_ip1 is False
    assert reason_ip1 == "ip_rate_limit"

    # IP 10.0.0.2 is still allowed
    allowed_ip2, reason_ip2, msg_ip2 = limiter.check_and_record("10.0.0.2")
    assert allowed_ip2 is True
    assert reason_ip2 is None
    assert msg_ip2 is None


def test_rate_limiter_daily_cap_and_reset() -> None:
    """Verify global daily request cap blocks across IPs and resets on the next UTC day."""
    clock = MockClock(datetime(2026, 1, 1, 10, 0, 0, tzinfo=UTC))
    limiter = RateLimiter(rate_limit_per_minute=5, daily_request_cap=6, clock=clock)

    # 5 requests from IP A
    for _ in range(5):
        allowed, _, _ = limiter.check_and_record("10.0.0.1")
        assert allowed is True

    # 1 request from IP B reaches daily cap (6)
    allowed_b, _, _ = limiter.check_and_record("10.0.0.2")
    assert allowed_b is True
    assert limiter.daily_count == 6

    # 7th request across system is blocked by daily cap (English)
    allowed_cap_en, reason_cap_en, msg_cap_en = limiter.check_and_record("10.0.0.3", lang="en")
    assert allowed_cap_en is False
    assert reason_cap_en == "daily_cap"
    assert msg_cap_en == (
        "Daily public demo quota (6 requests/day) reached. "
        "Please explore the pre-evaluated scenarios or try again tomorrow (UTC)."
    )

    # 8th request across system is blocked by daily cap (Portuguese)
    allowed_cap_pt, reason_cap_pt, msg_cap_pt = limiter.check_and_record("10.0.0.3", lang="pt")
    assert allowed_cap_pt is False
    assert reason_cap_pt == "daily_cap"
    assert msg_cap_pt == (
        "A cota diária da demonstração pública (6 requisições/dia) foi atingida. "
        "Explore os cenários pré-avaliados ou tente novamente amanhã (UTC)."
    )

    # Daily count is not incremented on cap denial
    assert limiter.daily_count == 6

    # Advance clock to next UTC day
    clock.advance(days=1)

    # Requests are allowed again and counter resets
    allowed_next_day, reason_next_day, msg_next_day = limiter.check_and_record("10.0.0.1")
    assert allowed_next_day is True
    assert reason_next_day is None
    assert msg_next_day is None
    assert limiter.daily_count == 1


def test_rate_limiter_default_clock() -> None:
    """Verify RateLimiter defaults to system UTC clock when none is provided."""
    limiter = RateLimiter(rate_limit_per_minute=5, daily_request_cap=200)
    allowed, reason, msg = limiter.check_and_record("127.0.0.1")
    assert allowed is True
    assert reason is None
    assert msg is None
    assert limiter.daily_count == 1


def test_extract_client_ip() -> None:
    """Verify client IP extraction from X-Forwarded-For and fallback host."""
    # Single IP in X-Forwarded-For
    assert extract_client_ip("203.0.113.195", None) == "203.0.113.195"

    # Multiple comma-separated IPs in X-Forwarded-For (takes first)
    assert extract_client_ip("203.0.113.195, 70.41.3.18, 150.172.238.178", None) == "203.0.113.195"

    # Leading/trailing whitespace in header
    assert extract_client_ip("   203.0.113.195   , 10.0.0.1 ", "127.0.0.1") == "203.0.113.195"

    # None header falls back to client host
    assert extract_client_ip(None, "192.168.1.50") == "192.168.1.50"

    # Empty header falls back to client host
    assert extract_client_ip("", "192.168.1.50") == "192.168.1.50"

    # Whitespace-only header falls back to client host
    assert extract_client_ip("   ", "192.168.1.50") == "192.168.1.50"

    # Header with only commas falls back to client host
    assert extract_client_ip(",,", "192.168.1.50") == "192.168.1.50"

    # None header and None host falls back to "unknown"
    assert extract_client_ip(None, None) == "unknown"

    # Empty header and None host falls back to "unknown"
    assert extract_client_ip("", None) == "unknown"
