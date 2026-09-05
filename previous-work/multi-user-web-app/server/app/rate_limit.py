from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import load_auth_config


def _redis_storage_uri() -> str:
    return load_auth_config()["REDIS_URL"]


# Redis-backed (not in-memory) so the limit is enforced correctly even if
# the app ever runs as more than one process/replica - ported from
# buzzkit's app/core/rate_limit.py. IP-keyed, matching TODO.md 1.8
# ("...from the same IP"), not buzzkit's separate username-keyed lockout
# (not ported - see TODO.md Phase 1's architecture note).
limiter = Limiter(key_func=get_remote_address, storage_uri=_redis_storage_uri())
