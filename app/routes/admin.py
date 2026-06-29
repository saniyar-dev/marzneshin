from typing import Optional, Annotated
import os
import secrets
import logging

import sqlalchemy
from fastapi import APIRouter
from fastapi import Depends, HTTPException, UploadFile, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from app.config.env import (
    BRAND_LOGOS_DIRECTORY,
    BRAND_LOGOS_URL_PREFIX,
    BRAND_LOGO_MAX_BYTES,
)
from app.db import Session, crud
from app.db.models import (
    Admin as DBAdmin,
    AdminBilling,
    AdminBillingEvent,
    Service,
    User,
)
from app.dependencies import AdminDep, SudoAdminDep, DBDep
from app.marznode.operations import update_user
from app.models.admin import (
    Admin,
    AdminBrandingModify,
    AdminCreate,
    AdminInDB,
    Token,
    AdminPartialModify,
    AdminResponse,
)
from app.models.billing import (
    AdminBillingCheckpointCreate,
    AdminBillingEventResponse,
    AdminBillingResponse,
)
from app.models.service import ServiceResponse
from app.models.user import UserResponse
from app.utils.auth import create_admin_token

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Admin"], prefix="/admins")


ALLOWED_LOGO_TYPES = {
    "image/png",
    "image/jpeg",
    "image/webp",
    "image/svg+xml",
}
ALLOWED_LOGO_EXTS = {"png", "jpg", "jpeg", "webp", "svg"}


def authenticate_admin(
    db: Session, username: str, password: str
) -> Optional[Admin]:
    dbadmin = crud.get_admin(db, username)
    if not dbadmin:
        return None

    return (
        dbadmin
        if AdminInDB.model_validate(dbadmin).verify_password(password)
        else None
    )


@router.get("", response_model=Page[AdminResponse])
def get_admins(db: DBDep, admin: SudoAdminDep, username: str | None = None):
    query = db.query(DBAdmin)
    if username:
        query = query.filter(DBAdmin.username.ilike(f"%{username}%"))
    return paginate(db, query)


@router.post("", response_model=Admin)
def create_admin(new_admin: AdminCreate, db: DBDep, admin: SudoAdminDep):
    try:
        dbadmin = crud.create_admin(db, new_admin)
    except sqlalchemy.exc.IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Admin already exists")

    return dbadmin


@router.get("/current", response_model=Admin)
def get_current_admin(admin: AdminDep):
    return admin


@router.put("/current/branding", response_model=AdminResponse)
def update_own_branding(
    branding: AdminBrandingModify, db: DBDep, admin: AdminDep
):
    dbadmin = crud.get_admin(db, admin.username)
    if not dbadmin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return crud.set_admin_branding(db, dbadmin, branding)


@router.post("/current/logo")
async def upload_own_logo(file: UploadFile, db: DBDep, admin: AdminDep):
    if file.content_type not in ALLOWED_LOGO_TYPES:
        raise HTTPException(status_code=415, detail="Unsupported image type")

    original = file.filename or ""
    ext = original.rsplit(".", 1)[-1].lower() if "." in original else ""
    if ext not in ALLOWED_LOGO_EXTS:
        raise HTTPException(
            status_code=415, detail="Unsupported file extension"
        )

    dbadmin = crud.get_admin(db, admin.username)
    if not dbadmin:
        raise HTTPException(status_code=404, detail="Admin not found")

    body = await file.read()
    if len(body) > BRAND_LOGO_MAX_BYTES:
        raise HTTPException(status_code=413, detail="Logo too large")

    os.makedirs(BRAND_LOGOS_DIRECTORY, exist_ok=True)
    filename = f"{dbadmin.id}_{secrets.token_hex(8)}.{ext}"
    with open(os.path.join(BRAND_LOGOS_DIRECTORY, filename), "wb") as f:
        f.write(body)

    crud.set_admin_branding(
        db, dbadmin, AdminBrandingModify(brand_logo_filename=filename)
    )

    return {
        "filename": filename,
        "url": f"{BRAND_LOGOS_URL_PREFIX}{filename}",
    }


@router.post("/token", response_model=Token)
def admin_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: DBDep
):
    if dbadmin := authenticate_admin(
        db, form_data.username, form_data.password
    ):
        return Token(
            is_sudo=dbadmin.is_sudo,
            access_token=create_admin_token(
                form_data.username, is_sudo=dbadmin.is_sudo
            ),
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.get("/{username}", response_model=AdminResponse)
def get_admin(
    username: str,
    db: DBDep,
    admin: SudoAdminDep,
):
    dbadmin = crud.get_admin(db, username)
    if not dbadmin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return dbadmin


@router.put("/{username}", response_model=AdminResponse)
def modify_admin(
    username: str,
    modified_admin: AdminPartialModify,
    db: DBDep,
    admin: SudoAdminDep,
):
    dbadmin = crud.get_admin(db, username)
    if not dbadmin:
        raise HTTPException(status_code=404, detail="Admin not found")

    # If a sudoer admin wants to edit another sudoer
    if username != admin.username and dbadmin.is_sudo:
        raise HTTPException(
            status_code=403,
            detail="You're not allowed to edit another sudoers account. Use fishy-cli instead.",
        )

    dbadmin = crud.update_admin(db, dbadmin, modified_admin)
    return dbadmin


@router.get("/{username}/services", response_model=Page[ServiceResponse])
def get_admin_services(username: str, db: DBDep, admin: SudoAdminDep):
    """
    Get user services
    """
    db_admin = crud.get_admin(db, username)
    if not db_admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    if db_admin.is_sudo or db_admin.all_services_access:
        query = db.query(Service)
    else:
        query = (
            db.query(Service)
            .join(Service.admins)
            .where(DBAdmin.id == db_admin.id)
        )

    return paginate(query)


@router.get("/{username}/users", response_model=Page[UserResponse])
def get_admin_users(username: str, db: DBDep, admin: SudoAdminDep):
    """
    Get user services
    """
    db_admin = crud.get_admin(db, username)
    if not db_admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    query = (
        db.query(User)
        .where(User.admin_id == db_admin.id)
        .filter(User.username.isnot(None))
    )

    return paginate(query)


@router.post("/{username}/disable_users", response_model=AdminResponse)
async def disable_users(username: str, db: DBDep, admin: SudoAdminDep):
    db_admin = crud.get_admin(db, username)
    if not db_admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    if db_admin.is_sudo and db_admin.username != admin.username:
        raise HTTPException(
            status_code=403,
            detail="You're not allowed.",
        )

    for user in crud.get_users(db, admin=db_admin, enabled=True):
        if user.activated:
            update_user(user, remove=True)
        user.enabled = False
        user.activated = False
    db.commit()

    return db_admin


@router.post("/{username}/enable_users", response_model=AdminResponse)
async def enable_users(username: str, db: DBDep, admin: SudoAdminDep):
    db_admin = crud.get_admin(db, username)
    if not db_admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    if db_admin.is_sudo and db_admin.username != admin.username:
        raise HTTPException(
            status_code=403,
            detail="You're not allowed.",
        )

    for user in crud.get_users(db, admin=db_admin, enabled=False):
        user.enabled = True
        if user.is_active:
            update_user(user)
            user.activated = True
    db.commit()

    return db_admin


@router.delete("/{username}")
def remove_admin(username: str, db: DBDep, admin: SudoAdminDep):
    dbadmin = crud.get_admin(db, username)
    if not dbadmin:
        raise HTTPException(status_code=404, detail="Admin not found")

    if dbadmin.is_sudo:
        raise HTTPException(
            status_code=403,
            detail="You're not allowed to delete sudoers accounts. Use fishy-cli instead.",
        )

    crud.remove_admin(db, dbadmin)
    return {}


def _build_billing_response(
    db, dbadmin: DBAdmin, billing: AdminBilling | None
) -> AdminBillingResponse:
    total = billing.total_billable_bytes if billing else 0
    checkpoint_bytes = billing.last_checkpoint_bytes if billing else None
    unbilled = total - (checkpoint_bytes or 0)
    if unbilled < 0:
        unbilled = 0
    return AdminBillingResponse(
        admin_id=dbadmin.id,
        username=dbadmin.username,
        total_billable_bytes=total,
        last_checkpoint_at=(billing.last_checkpoint_at if billing else None),
        last_checkpoint_bytes=checkpoint_bytes,
        last_checkpoint_note=(
            billing.last_checkpoint_note if billing else None
        ),
        unbilled_bytes=unbilled,
        event_count=(
            crud.count_billing_events(db, dbadmin.id) if billing else 0
        ),
    )


@router.get("/current/billing", response_model=AdminBillingResponse)
def get_current_admin_billing(db: DBDep, admin: AdminDep):
    dbadmin = crud.get_admin(db, admin.username)
    if not dbadmin:
        raise HTTPException(status_code=404, detail="Admin not found")
    billing = crud.get_billing(db, dbadmin.id)
    return _build_billing_response(db, dbadmin, billing)


@router.get(
    "/current/billing/events",
    response_model=list[AdminBillingEventResponse],
)
def get_current_admin_billing_events(
    db: DBDep,
    admin: AdminDep,
    event_type: str | None = None,
    limit: int = 100,
    offset: int = 0,
):
    dbadmin = crud.get_admin(db, admin.username)
    if not dbadmin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return crud.get_billing_events(
        db,
        dbadmin.id,
        offset=offset,
        limit=limit,
        event_type=event_type,
    )


@router.get("/{username}/billing", response_model=AdminBillingResponse)
def get_admin_billing(username: str, db: DBDep, admin: SudoAdminDep):
    dbadmin = crud.get_admin(db, username)
    if not dbadmin:
        raise HTTPException(status_code=404, detail="Admin not found")
    billing = crud.get_billing(db, dbadmin.id)
    return _build_billing_response(db, dbadmin, billing)


@router.get(
    "/{username}/billing/events",
    response_model=list[AdminBillingEventResponse],
)
def get_admin_billing_events(
    username: str,
    db: DBDep,
    admin: SudoAdminDep,
    event_type: str | None = None,
    limit: int = 100,
    offset: int = 0,
):
    dbadmin = crud.get_admin(db, username)
    if not dbadmin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return crud.get_billing_events(
        db,
        dbadmin.id,
        offset=offset,
        limit=limit,
        event_type=event_type,
    )


@router.post(
    "/{username}/billing/checkpoint",
    response_model=AdminBillingResponse,
)
def set_admin_billing_checkpoint(
    username: str,
    payload: AdminBillingCheckpointCreate,
    db: DBDep,
    admin: SudoAdminDep,
):
    dbadmin = crud.get_admin(db, username)
    if not dbadmin:
        raise HTTPException(status_code=404, detail="Admin not found")

    if dbadmin.is_sudo:
        raise HTTPException(
            status_code=403,
            detail="Checkpoints are only for non-sudo admins.",
        )

    billing = crud.set_billing_checkpoint(db, dbadmin.id, payload.note)
    logger.info(
        "Billing checkpoint set for admin `%s` at %s bytes (note: %s)",
        dbadmin.username,
        billing.last_checkpoint_bytes,
        payload.note,
    )
    return _build_billing_response(db, dbadmin, billing)
