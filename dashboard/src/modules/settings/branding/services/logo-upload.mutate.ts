import { useMutation } from "@tanstack/react-query";
import { fetch, queryClient } from "@marzneshin/common/utils";
import { toast } from "sonner";
import i18n from "@marzneshin/features/i18n";
import { currentAdminQueryKey } from "@marzneshin/modules/admins";
import type { LogoUploadResponse } from "../branding.type";

export async function uploadLogo(file: File): Promise<LogoUploadResponse> {
    const formData = new FormData();
    formData.append("file", file);
    return fetch("/admins/current/logo", {
        method: "post",
        body: formData,
    });
}

const handleError = (error: unknown) => {
    const message =
        (error as { data?: { detail?: string } })?.data?.detail ??
        i18n.t("events.update.error");
    toast.error(message);
};

const handleSuccess = () => {
    queryClient.invalidateQueries({ queryKey: currentAdminQueryKey });
};

export const useLogoUploadMutation = () => {
    return useMutation({
        mutationKey: ["branding", "logo"],
        mutationFn: uploadLogo,
        onError: handleError,
        onSuccess: handleSuccess,
    });
};