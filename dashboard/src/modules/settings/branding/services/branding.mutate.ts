import { useMutation } from "@tanstack/react-query";
import { fetch, queryClient } from "@fishy/common/utils";
import { toast } from "sonner";
import i18n from "@fishy/features/i18n";
import { currentAdminQueryKey } from "@fishy/modules/admins";
import type { BrandingType } from "../branding.type";

export type BrandingPayload = Partial<BrandingType>;

export async function updateBranding(payload: BrandingPayload): Promise<BrandingType> {
    return fetch("/admins/current/branding", {
        method: "put",
        body: payload,
    });
}

const handleError = (error: unknown) => {
    const message =
        (error as { data?: { detail?: string } })?.data?.detail ??
        i18n.t("events.update.error");
    toast.error(message);
};

const handleSuccess = () => {
    toast.success(
        i18n.t("events.update.success.title", { name: i18n.t("branding") }),
        { description: i18n.t("events.update.success.desc") },
    );
    queryClient.invalidateQueries({ queryKey: currentAdminQueryKey });
};

export const useBrandingMutation = () => {
    return useMutation({
        mutationKey: ["branding"],
        mutationFn: updateBranding,
        onError: handleError,
        onSuccess: handleSuccess,
    });
};