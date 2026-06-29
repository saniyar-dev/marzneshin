import { FC } from "react";
import { Page, VStack } from "@fishy/common/components";
import { useTranslation } from "react-i18next";
import { createLazyFileRoute } from "@tanstack/react-router";
import {
    AdminBillingCardForCurrent,
    AdminBillingEventsTable,
} from "@fishy/modules/admins";

export const BillingPage: FC = () => {
    const { t } = useTranslation();
    return (
        <Page
            title={t("page.admins.billing.title")}
            className="sm:flex flex-col lg:grid grid-cols-1 gap-3"
        >
            <VStack className="gap-3">
                <AdminBillingCardForCurrent />
                <AdminBillingEventsTable username={null} />
            </VStack>
        </Page>
    );
};

export const Route = createLazyFileRoute("/_dashboard/billing")({
    component: BillingPage,
});
