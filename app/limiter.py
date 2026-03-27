from fastapi import Request
from slowapi import Limiter


def _get_client_ip(request: Request) -> str:
    """
    Return the real visitor IP.
    Cloudflare sets CF-Connecting-IP; behind a plain reverse proxy the first
    value in X-Forwarded-For is used; otherwise fall back to the socket peer.
    """
    cf_ip = request.headers.get("CF-Connecting-IP")
    if cf_ip:
        return cf_ip
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


limiter = Limiter(key_func=_get_client_ip)
