import { useQuery } from "@tanstack/react-query";
import { fetch } from "@fishy/common/utils";
import { NodesQueryFetchKey } from "@fishy/modules/nodes";

export async function fetchCertificate(): Promise<string> {
    return fetch('/nodes/settings').then((settings) => {
        return settings.certificate;
    });
}

export const CertificateQueryFetchKey = "settings";

export const useCertificateQuery = () => {
    return useQuery({
        queryKey: [NodesQueryFetchKey, CertificateQueryFetchKey],
        queryFn: fetchCertificate,
        initialData: ''
    })
}
