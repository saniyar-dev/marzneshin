export type AdminBillingEventKind =
    | "initial_allocation"
    | "limit_increase"
    | "manual_reset"
    | "auto_reset";

export interface AdminBillingEventType {
    id: number;
    admin_id: number;
    user_id: number;
    event_type: AdminBillingEventKind;
    bytes_amount: number;
    occurred_at: string;
    note: string | null;
}

export interface AdminBillingType {
    admin_id: number;
    username: string;
    total_billable_bytes: number;
    last_checkpoint_at: string | null;
    last_checkpoint_bytes: number | null;
    last_checkpoint_note: string | null;
    unbilled_bytes: number;
    event_count: number;
}
