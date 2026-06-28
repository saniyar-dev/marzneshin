"""
Marzban-compatible subscription token codec.

Matches the exact algorithm in Marzban's
`app/utils/jwt.py:create_subscription_token` and
`get_subscription_payload` so that any Marzban-issued subscription URL
continues to work against Fishy Service's `/sub/{token}` route after
migration.
"""

from base64 import b64decode, b64encode
from datetime import datetime
from hashlib import sha256
from math import ceil
from time import time
from typing import Optional


def create_marzban_subscription_token(
    username: str, jwt_secret: str
) -> str:
    """
    Generate a Marzban-compatible subscription token.

    Format (matches Marzban's `create_subscription_token` in
    `Marzban/app/utils/jwt.py:47-57`):
        b64url(username,ceil(time.time())) + b64url(sha256(token+secret))[:10]
    """
    data = username + "," + str(ceil(time()))
    data_b64 = (
        b64encode(data.encode("utf-8"), altchars=b"-_")
        .decode("utf-8")
        .rstrip("=")
    )
    sig = (
        b64encode(
            sha256((data_b64 + jwt_secret).encode("utf-8")).digest(),
            altchars=b"-_",
        )
        .decode("utf-8")[:10]
    )
    return data_b64 + sig


def decode_marzban_subscription_token(
    token: str, jwt_secret: str
) -> Optional[str]:
    """
    Verify a Marzban-style subscription token signature and return
    the embedded username. Returns None if the token is invalid or
    the signature doesn't match.
    """
    if not token or len(token) < 15 or not jwt_secret:
        return None

    u_token = token[:-10]
    u_signature = token[-10:]

    try:
        u_token_bytes = b64decode(
            u_token.encode("utf-8")
            + b"=" * (-len(u_token.encode("utf-8")) % 4),
            altchars=b"-_",
            validate=True,
        )
        u_token_dec = u_token_bytes.decode("utf-8")
    except Exception:
        return None

    u_token_resign = (
        b64encode(
            sha256((u_token + jwt_secret).encode("utf-8")).digest(),
            altchars=b"-_",
        )
        .decode("utf-8")[:10]
    )
    if u_signature != u_token_resign:
        return None

    try:
        username, _created_at = u_token_dec.split(",", 1)
    except ValueError:
        return None
    return username


def get_marzban_token_payload(
    token: str, jwt_secret: str
) -> Optional[dict]:
    """
    Same as `decode_marzban_subscription_token` but also returns the
    original token-creation timestamp as a `datetime`.
    """
    if not token or len(token) < 15 or not jwt_secret:
        return None

    u_token = token[:-10]
    u_signature = token[-10:]

    try:
        u_token_bytes = b64decode(
            u_token.encode("utf-8")
            + b"=" * (-len(u_token.encode("utf-8")) % 4),
            altchars=b"-_",
            validate=True,
        )
        u_token_dec = u_token_bytes.decode("utf-8")
    except Exception:
        return None

    u_token_resign = (
        b64encode(
            sha256((u_token + jwt_secret).encode("utf-8")).digest(),
            altchars=b"-_",
        )
        .decode("utf-8")[:10]
    )
    if u_signature != u_token_resign:
        return None

    try:
        username, created_at = u_token_dec.split(",", 1)
        created_at_dt = datetime.utcfromtimestamp(int(created_at))
    except (ValueError, TypeError):
        return None
    return {"username": username, "created_at": created_at_dt}
