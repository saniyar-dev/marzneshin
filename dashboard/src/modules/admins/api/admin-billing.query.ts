import {
    queryOptions,
    useMutation,
    useQuery,
    useQueryClient,
} from "@tanstack/react-query";
import { fetch } from "@fishy/common/utils";
import {
    AdminBillingEventKind,
    AdminBillingEventType,
    AdminBillingType,
} from "../types";

export const AdminBillingFetchKey = "admin-billing";

export const adminBillingQueryOptions = ({
    username,
}: {
    username: string | null;
}) =>
    queryOptions({
        queryKey: [AdminBillingFetchKey, username],
        queryFn: async (): Promise<AdminBillingType> => {
            return fetch(
                username
                    ? `/admins/${username}/billing`
                    : `/admins/current/billing`,
            );
        },
    });

export const useAdminBillingQuery = ({
    username,
}: {
    username: string | null;
}) => useQuery(adminBillingQueryOptions({ username }));

export const adminBillingEventsQueryOptions = ({
    username,
    eventType,
    limit = 100,
    offset = 0,
}: {
    username: string | null;
    eventType?: AdminBillingEventKind;
    limit?: number;
    offset?: number;
}) =>
    queryOptions({
        queryKey: [
            AdminBillingFetchKey,
            "events",
            username,
            eventType ?? "",
            limit,
            offset,
        ],
        queryFn: async (): Promise<AdminBillingEventType[]> => {
            const path = username
                ? `/admins/${username}/billing/events`
                : `/admins/current/billing/events`;
            return fetch(path, {
                query: { event_type: eventType, limit, offset },
            });
        },
    });

export const useAdminBillingEventsQuery = ({
    username,
    eventType,
    limit = 100,
    offset = 0,
}: {
    username: string | null;
    eventType?: AdminBillingEventKind;
    limit?: number;
    offset?: number;
}) =>
    useQuery(
        adminBillingEventsQueryOptions({
            username,
            eventType,
            limit,
            offset,
        }),
    );

export const useSetAdminBillingCheckpointMutation = () => {
    const qc = useQueryClient();
    return useMutation({
        mutationFn: async ({
            username,
            note,
        }: {
            username: string;
            note?: string;
        }): Promise<AdminBillingType> => {
            return fetch(`/admins/${username}/billing/checkpoint`, {
                method: "POST",
                body: { note },
            });
        },
        onSuccess: (_data, vars) => {
            qc.invalidateQueries({
                queryKey: [AdminBillingFetchKey, vars.username],
            });
            qc.invalidateQueries({
                queryKey: [AdminBillingFetchKey, "events", vars.username],
            });
        },
    });
};
