import { Page, VStack } from "@marzneshin/common/components";
import { BrandingWidget } from "@marzneshin/modules/settings";
import { createLazyFileRoute } from "@tanstack/react-router";
import { useTranslation } from "react-i18next";

export const Branding = () => {
    const { t } = useTranslation();
    return (
        <Page
            title={t("branding")}
            className="sm:flex flex-col lg:grid grid-cols-2 gap-3 h-full"
        >
            <VStack className="gap-3">
                <BrandingWidget />
            </VStack>
        </Page>
    );
};

export const Route = createLazyFileRoute("/_dashboard/branding")({
    component: Branding,
});
