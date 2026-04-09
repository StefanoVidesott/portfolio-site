import ipaddress

from fastapi import Request
from slowapi import Limiter

# ---------------------------------------------------------------------------
# Cloudflare IP ranges — fallback list embedded for fail-closed behaviour.
#
# At startup the lifespan in main.py attempts to fetch the authoritative list
# from https://www.cloudflare.com/ips-v4 and https://www.cloudflare.com/ips-v6
# and stores parsed networks in app.state.cloudflare_networks.  If that fetch
# fails this module-level list is used instead so the application still starts.
#
# Source: https://www.cloudflare.com/ips-v4  /  https://www.cloudflare.com/ips-v6
# Last verified: 2026-04-09  — update when Cloudflare publishes range changes.
# ---------------------------------------------------------------------------
_CF_FALLBACK_RANGES: list[str] = [
    # IPv4
    "173.245.48.0/20",
    "103.21.244.0/22",
    "103.22.200.0/22",
    "103.31.4.0/22",
    "141.101.64.0/18",
    "108.162.192.0/18",
    "190.93.240.0/20",
    "188.114.96.0/20",
    "197.234.240.0/22",
    "198.41.128.0/17",
    "162.158.0.0/15",
    "104.16.0.0/13",
    "104.24.0.0/14",
    "172.64.0.0/13",
    "131.0.72.0/22",
    # IPv6
    "2400:cb00::/32",
    "2606:4700::/32",
    "2803:f800::/32",
    "2405:b500::/32",
    "2405:8100::/32",
    "2a06:98c0::/29",
    "2c0f:f248::/32",
]

CF_FALLBACK_NETWORKS: list[ipaddress.IPv4Network | ipaddress.IPv6Network] = [
    ipaddress.ip_network(cidr) for cidr in _CF_FALLBACK_RANGES
]


def _is_from_cloudflare(
    peer_ip: str,
    networks: list[ipaddress.IPv4Network | ipaddress.IPv6Network],
) -> bool:
    """Return True iff peer_ip falls within a known Cloudflare-owned CIDR.

    Uses the network list loaded at startup (app.state.cloudflare_networks),
    which is fetched from Cloudflare's authoritative IP list endpoints and falls
    back to the hardcoded CF_FALLBACK_NETWORKS if that fetch failed.
    """
    try:
        addr = ipaddress.ip_address(peer_ip)
    except ValueError:
        return False
    return any(addr in net for net in networks)


def _get_client_ip(request: Request) -> str:
    """Return the real visitor IP, trusting Cloudflare headers only when the
    TCP peer address is provably a Cloudflare IP.

    Attack surface closed by this function:
    - An attacker connecting directly to the origin (i.e. not through Cloudflare)
      cannot forge CF-Connecting-IP or X-Forwarded-For to impersonate a different
      IP, because neither header is trusted unless the socket-level peer address
      is inside a verified Cloudflare CIDR.
    - If Cloudflare's range list failed to load at startup, the module-level
      fallback is used so the control remains operative.
    """
    peer_ip: str = request.client.host if request.client else ""

    # Resolve the active network list — prefer the one fetched at startup.
    try:
        cf_networks: list = request.app.state.cloudflare_networks
    except AttributeError:
        # app.state not yet populated (e.g. test client before lifespan runs).
        cf_networks = CF_FALLBACK_NETWORKS

    if _is_from_cloudflare(peer_ip, cf_networks):
        # Request is arriving from a Cloudflare edge node: the CF-Connecting-IP
        # header is injected by Cloudflare itself and can be trusted.
        cf_ip = request.headers.get("CF-Connecting-IP", "").strip()
        if cf_ip:
            return cf_ip

    # Direct connection or non-Cloudflare proxy: trust only the socket peer.
    # X-Forwarded-For is deliberately ignored here — it is client-controlled
    # and must never be used as a security boundary without prior verification.
    return peer_ip or "unknown"


limiter = Limiter(key_func=_get_client_ip)
