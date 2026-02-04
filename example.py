"""Usage example for rate limiter library."""

from rate_limiter import FixedWindowRateLimiter, TokenBucketRateLimiter


def run_fixed_window_demo() -> None:
    limiter = FixedWindowRateLimiter(max_requests=3, window_seconds=5)
    for client_id in ("alice", "bob"):
        print(f"Fixed window for {client_id}:")
        for i in range(5):
            allowed = limiter.allow_request(client_id)
            print(f"  request {i + 1}: {allowed}")
        print()


def run_token_bucket_demo() -> None:
    limiter = TokenBucketRateLimiter(capacity=2, refill_rate=0.5)
    for client_id in ("alice", "bob"):
        print(f"Token bucket for {client_id}:")
        for i in range(4):
            allowed = limiter.allow_request(client_id)
            print(f"  request {i + 1}: {allowed}")
        print()


if __name__ == "__main__":
    run_fixed_window_demo()
    run_token_bucket_demo()
