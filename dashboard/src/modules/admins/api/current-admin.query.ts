import { useQuery } from "@tanstack/react-query";
import { fetch } from "@marzneshin/common/utils";
import type { AdminType } from "../types";

export async function fetchCurrentAdmin(): Promise<AdminType> {
    return fetch(`/admins/current`);
}

export const currentAdminQueryKey = ["admins", "current"] as const;

export const useCurrentAdminQuery = () => {
    return useQuery({
        queryKey: currentAdminQueryKey,
        queryFn: fetchCurrentAdmin,
    });
};