from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class AdminBillingEventType(StrEnum):
    INITIAL_ALLOCATION = "initial_allocation"
    LIMIT_INCREASE = "limit_increase"
    MANUAL_RESET = "manual_reset"
    AUTO_RESET = "auto_reset"


class AdminBillingEventBase(BaseModel):
    event_type: AdminBillingEventType
    bytes_amount: int = Field(ge=0)
    note: str | None = Field(None, max_length=512)
    model_config = ConfigDict(from_attributes=True)


class AdminBillingEventResponse(AdminBillingEventBase):
    id: int
    user_id: int
    occurred_at: datetime


class AdminBillingResponse(BaseModel):
    admin_id: int
    username: str
    total_billable_bytes: int
    last_checkpoint_at: datetime | None
    last_checkpoint_bytes: int | None
    last_checkpoint_note: str | None
    unbilled_bytes: int
    event_count: int
    model_config = ConfigDict(from_attributes=True)


class AdminBillingCheckpointCreate(BaseModel):
    note: str | None = Field(None, max_length=512)
