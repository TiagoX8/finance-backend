import os
import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import HTTPException, Request, status

LOGIN_MAX_ATTEMPTS = int(os.getenv("LOGIN_RATE_LIMIT_ATTEMPTS", "10"))
LOGIN_WINDOW_SECONDS = int(os.getenv("LOGIN_RATE_LIMIT_WINDOW", "300"))
REGISTER_MAX_ATTEMPTS = int(os.getenv("REGISTER_RATE_LIMIT_ATTEMPTS", "5"))
REGISTER_WINDOW_SECONDS = int(os.getenv("REGISTER_RATE_LIMIT_WINDOW", "3600"))


class RateLimiter:
    """Janela deslizante em memória, por processo.

    Suficiente para conter força bruta em um deploy de instância única. Com
    múltiplas réplicas cada uma tem sua própria contagem, e o limite efetivo
    passa a ser o limite multiplicado pelo número de réplicas.
    """

    def __init__(self, max_attempts: int, window_seconds: int):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def retry_after(self, key: str) -> int | None:
        now = time.monotonic()

        with self._lock:
            hits = self._hits[key]

            while hits and now - hits[0] > self.window_seconds:
                hits.popleft()

            if len(hits) >= self.max_attempts:
                return max(1, int(self.window_seconds - (now - hits[0])))

            hits.append(now)

            if len(self._hits) > 10_000:
                self._evict(now)

            return None

    def reset(self, key: str) -> None:
        with self._lock:
            self._hits.pop(key, None)

    def _evict(self, now: float) -> None:
        for key in [k for k, hits in self._hits.items() if not hits or now - hits[-1] > self.window_seconds]:
            del self._hits[key]


login_limiter = RateLimiter(LOGIN_MAX_ATTEMPTS, LOGIN_WINDOW_SECONDS)
register_limiter = RateLimiter(REGISTER_MAX_ATTEMPTS, REGISTER_WINDOW_SECONDS)


def client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    return request.client.host if request.client else "unknown"


def enforce(limiter: RateLimiter, key: str) -> None:
    retry_after = limiter.retry_after(key)

    if retry_after is not None:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas tentativas. Tente novamente mais tarde.",
            headers={"Retry-After": str(retry_after)},
        )
