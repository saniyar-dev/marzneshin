from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .base import Base, SessionLocal, engine  # noqa
from .crud import (
    count_billing_events,
    create_admin,
    create_user,
    get_admin,
    get_admins,
    get_billing,
    get_billing_events,
    get_jwt_secret_key,
    ensure_node_inbounds,
    get_system_usage,
    get_tls_certificate,
    get_user,
    get_user_by_id,
    get_users,
    get_users_count,
    record_billing_event,
    remove_admin,
    remove_user,
    revoke_user_sub,
    set_admin_branding,
    set_billing_checkpoint,
    set_owner,
    update_admin,
    update_user,
    update_user_status,
    update_user_sub,
)
from .models import JWT, System, User  # noqa


class GetDB:  # Context Manager
    def __init__(self):
        self.db = SessionLocal()

    def __enter__(self):
        return self.db

    def __exit__(self, _, exc_value, traceback):
        if isinstance(exc_value, SQLAlchemyError):
            self.db.rollback()  # rollback on exception

        self.db.close()


__all__ = [
    "get_user",
    "get_user_by_id",
    "get_users",
    "get_users_count",
    "create_user",
    "remove_user",
    "update_user",
    "update_user_status",
    "update_user_sub",
    "revoke_user_sub",
    "set_owner",
    "get_system_usage",
    "get_jwt_secret_key",
    "get_tls_certificate",
    "get_admin",
    "create_admin",
    "update_admin",
    "remove_admin",
    "get_admins",
    "set_admin_branding",
    "get_billing",
    "get_billing_events",
    "count_billing_events",
    "record_billing_event",
    "set_billing_checkpoint",
    "GetDB",
    "User",
    "System",
    "JWT",
    "Base",
    "Session",
]
