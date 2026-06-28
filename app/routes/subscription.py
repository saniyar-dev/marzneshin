import re
from collections import defaultdict

from fastapi import APIRouter
from fastapi import Header, HTTPException, Path, Request, Response
from starlette.responses import HTMLResponse

from app.config.env import MARZBAN_JWT_TOKEN
from app.db import crud
from app.db.models import Settings, User
from app.dependencies import DBDep, SubUserDep, StartDateDep, EndDateDep
from app.models.settings import SubscriptionSettings
from app.models.system import TrafficUsageSeries
from app.models.user import UserResponse
from app.utils.marzban_token import decode_marzban_subscription_token
from app.utils.share import (
    encode_title,
    generate_subscription,
    generate_subscription_template,
)

router = APIRouter(prefix="/sub", tags=["Subscription"])


config_mimetype = defaultdict(
    lambda: "text/plain",
    {
        "links": "text/plain",
        "base64-links": "text/plain",
        "sing-box": "application/json",
        "xray": "application/json",
        "clash": "text/yaml",
        "clash-meta": "text/yaml",
        "template": "text/html",
        "block": "text/plain",
    },
)


def get_subscription_user_info(user: UserResponse) -> dict:
    return {
        "upload": 0,
        "download": user.used_traffic,
        "total": user.data_limit or 0,
        "expire": (
            int(user.expire_date.timestamp())
            if user.expire_strategy == "fixed_date"
            else 0
        ),
    }


def _render_subscription(db_user: User, db, request: Request, user_agent: str):
    user: UserResponse = UserResponse.model_validate(db_user)

    crud.update_user_sub(db, db_user, user_agent)

    subscription_settings = SubscriptionSettings.model_validate(
        db.query(Settings.subscription).first()[0]
    )

    if (
        subscription_settings.template_on_acceptance
        and "text/html" in request.headers.get("Accept", [])
    ):
        return HTMLResponse(
            generate_subscription_template(db_user, subscription_settings)
        )

    response_headers = {
        "content-disposition": f'attachment; filename="{user.username}"',
        "profile-web-page-url": str(request.url),
        "support-url": subscription_settings.support_link,
        "profile-title": encode_title(subscription_settings.profile_title),
        "profile-update-interval": str(subscription_settings.update_interval),
        "subscription-userinfo": "; ".join(
            f"{key}={val}"
            for key, val in get_subscription_user_info(user).items()
        ),
    }

    for rule in subscription_settings.rules:
        if re.match(rule.pattern, user_agent):
            if rule.result.value == "template":
                return HTMLResponse(
                    generate_subscription_template(
                        db_user, subscription_settings
                    )
                )
            elif rule.result.value == "block":
                raise HTTPException(404)
            elif rule.result.value == "base64-links":
                b64 = True
                config_format = "links"
            else:
                b64 = False
                config_format = rule.result.value

            conf = generate_subscription(
                user=db_user,
                config_format=config_format,
                as_base64=b64,
                use_placeholder=not user.is_active
                and subscription_settings.placeholder_if_disabled,
                placeholder_remark=subscription_settings.placeholder_remark,
                shuffle=subscription_settings.shuffle_configs,
            )
            return Response(
                content=conf,
                media_type=config_mimetype[rule.result],
                headers=response_headers,
            )


def _render_subscription_with_client_type(
    db_user: User, db, request: Request, client_type: str
):
    user: UserResponse = UserResponse.model_validate(db_user)

    subscription_settings = SubscriptionSettings.model_validate(
        db.query(Settings.subscription).first()[0]
    )

    response_headers = {
        "content-disposition": f'attachment; filename="{user.username}"',
        "profile-web-page-url": str(request.url),
        "support-url": subscription_settings.support_link,
        "profile-title": encode_title(subscription_settings.profile_title),
        "profile-update-interval": str(subscription_settings.update_interval),
        "subscription-userinfo": "; ".join(
            f"{key}={val}"
            for key, val in get_subscription_user_info(user).items()
        ),
    }

    conf = generate_subscription(
        user=db_user,
        config_format="links" if client_type == "v2ray" else client_type,
        as_base64=client_type == "v2ray",
        use_placeholder=not user.is_active
        and subscription_settings.placeholder_if_disabled,
        placeholder_remark=subscription_settings.placeholder_remark,
        shuffle=subscription_settings.shuffle_configs,
    )
    return Response(
        content=conf,
        media_type=client_type_mime_type[client_type],
        headers=response_headers,
    )


# Legacy {username}/{key} routes — must be declared BEFORE {token}
# so FastAPI matches the two-segment pattern first.
@router.get("/{username}/{key}")
def user_subscription(
    db_user: SubUserDep,
    request: Request,
    db: DBDep,
    user_agent: str = Header(default=""),
):
    """
    Subscription link, result format depends on subscription settings
    """
    return _render_subscription(db_user, db, request, user_agent)


@router.get("/{username}/{key}/info", response_model=UserResponse)
def user_subscription_info(db_user: SubUserDep):
    return db_user


@router.get("/{username}/{key}/usage", response_model=TrafficUsageSeries)
def user_get_usage(
    db_user: SubUserDep,
    db: DBDep,
    start_date: StartDateDep,
    end_date: EndDateDep,
):
    per_day = (end_date - start_date).total_seconds() > 3 * 86400
    return crud.get_user_total_usage(
        db, db_user, start_date, end_date, per_day=per_day
    )


client_type_mime_type = {
    "sing-box": "application/json",
    "wireguard": "application/json",
    "clash-meta": "text/yaml",
    "clash": "text/yaml",
    "xray": "application/json",
    "v2ray": "text/plain",
    "links": "text/plain",
}


@router.get("/{username}/{key}/{client_type}")
def user_subscription_with_client_type(
    db: DBDep,
    db_user: SubUserDep,
    request: Request,
    client_type: str = Path(
        regex="^(sing-box|clash-meta|clash|xray|v2ray|links|wireguard)$"
    ),
):
    """
    Subscription by client type; v2ray, xray, sing-box, clash and clash-meta formats supported
    """
    return _render_subscription_with_client_type(
        db_user, db, request, client_type
    )


# Token-based routes — single path segment after /sub/.
# Compatible with Marzban-style subscription URLs.
def _resolve_user_by_token(token: str, db) -> User | None:
    # Fast path: exact match against stored sub_token (used by
    # Fishy Service's own subscription_url).
    db_user = crud.get_user_by_sub_token(db, token)
    if db_user:
        return db_user

    # Slow path: decode the Marzban-style token (uses
    # MARZBAN_JWT_TOKEN) to recover the original username, then
    # look it up by `marzban_username`. This makes every existing
    # Marzban-issued URL continue to work after migration.
    if not MARZBAN_JWT_TOKEN:
        return None
    username = decode_marzban_subscription_token(token, MARZBAN_JWT_TOKEN)
    if not username:
        return None
    return crud.get_user_by_marzban_username(db, username)


@router.get("/{token}")
def user_subscription_by_token(
    token: str,
    request: Request,
    db: DBDep,
    user_agent: str = Header(default=""),
):
    """
    Marzban-compatible subscription link. Resolves user by either
    the stored `sub_token` (newly generated) or by decoding the
    token against `MARZBAN_JWT_TOKEN` and looking up the user by
    their original `marzban_username` (preserves URLs issued
    before migration).
    """
    db_user = _resolve_user_by_token(token, db)
    if not db_user:
        raise HTTPException(404)
    return _render_subscription(db_user, db, request, user_agent)


@router.get("/{token}/info", response_model=UserResponse)
def user_subscription_by_token_info(token: str, db: DBDep):
    db_user = _resolve_user_by_token(token, db)
    if not db_user:
        raise HTTPException(404)
    return db_user


@router.get("/{token}/usage", response_model=TrafficUsageSeries)
def user_subscription_by_token_usage(
    token: str,
    db: DBDep,
    start_date: StartDateDep,
    end_date: EndDateDep,
):
    db_user = _resolve_user_by_token(token, db)
    if not db_user:
        raise HTTPException(404)
    per_day = (end_date - start_date).total_seconds() > 3 * 86400
    return crud.get_user_total_usage(
        db, db_user, start_date, end_date, per_day=per_day
    )


@router.get("/{token}/{client_type}")
def user_subscription_by_token_with_client_type(
    token: str,
    request: Request,
    db: DBDep,
    client_type: str = Path(
        regex="^(sing-box|clash-meta|clash|xray|v2ray|links|wireguard)$"
    ),
):
    db_user = _resolve_user_by_token(token, db)
    if not db_user:
        raise HTTPException(404)
    return _render_subscription_with_client_type(
        db_user, db, request, client_type
    )
