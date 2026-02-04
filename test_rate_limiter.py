import unittest

from rate_limiter import FixedWindowRateLimiter, TokenBucketRateLimiter


class FakeTime:
    def __init__(self, start: float = 0.0) -> None:
        self._now = start

    def __call__(self) -> float:
        return self._now

    def advance(self, seconds: float) -> None:
        self._now += seconds


class FixedWindowRateLimiterTests(unittest.TestCase):
    def test_allows_within_window(self) -> None:
        fake_time = FakeTime()
        limiter = FixedWindowRateLimiter(
            max_requests=2,
            window_seconds=10,
            time_func=fake_time,
        )

        self.assertTrue(limiter.allow_request("client"))
        self.assertTrue(limiter.allow_request("client"))
        self.assertFalse(limiter.allow_request("client"))

    def test_resets_after_window(self) -> None:
        fake_time = FakeTime()
        limiter = FixedWindowRateLimiter(
            max_requests=1,
            window_seconds=5,
            time_func=fake_time,
        )

        self.assertTrue(limiter.allow_request("client"))
        self.assertFalse(limiter.allow_request("client"))

        fake_time.advance(5)
        self.assertTrue(limiter.allow_request("client"))

    def test_tracks_clients_independently(self) -> None:
        fake_time = FakeTime()
        limiter = FixedWindowRateLimiter(
            max_requests=1,
            window_seconds=5,
            time_func=fake_time,
        )

        self.assertTrue(limiter.allow_request("alice"))
        self.assertTrue(limiter.allow_request("bob"))
        self.assertFalse(limiter.allow_request("alice"))
        self.assertFalse(limiter.allow_request("bob"))


class TokenBucketRateLimiterTests(unittest.TestCase):
    def test_allows_until_capacity(self) -> None:
        fake_time = FakeTime()
        limiter = TokenBucketRateLimiter(
            capacity=2,
            refill_rate=1.0,
            time_func=fake_time,
        )

        self.assertTrue(limiter.allow_request("client"))
        self.assertTrue(limiter.allow_request("client"))
        self.assertFalse(limiter.allow_request("client"))

    def test_refills_over_time(self) -> None:
        fake_time = FakeTime()
        limiter = TokenBucketRateLimiter(
            capacity=1,
            refill_rate=1.0,
            time_func=fake_time,
        )

        self.assertTrue(limiter.allow_request("client"))
        self.assertFalse(limiter.allow_request("client"))

        fake_time.advance(1.0)
        self.assertTrue(limiter.allow_request("client"))

    def test_tracks_clients_independently(self) -> None:
        fake_time = FakeTime()
        limiter = TokenBucketRateLimiter(
            capacity=1,
            refill_rate=1.0,
            time_func=fake_time,
        )

        self.assertTrue(limiter.allow_request("alice"))
        self.assertTrue(limiter.allow_request("bob"))
        self.assertFalse(limiter.allow_request("alice"))
        self.assertFalse(limiter.allow_request("bob"))


if __name__ == "__main__":
    unittest.main()
