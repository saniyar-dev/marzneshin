import { SectionWidget } from "@fishy/common/components";
import { BrandingForm } from "@fishy/modules/settings/branding";
import { useTranslation } from "react-i18next";

export const BrandingWidget = () => {
    const { t } = useTranslation();
    return (
        <SectionWidget
            title={t("page.branding.title")}
            description={t("page.branding.description")}
            content={<BrandingForm />}
        />
    );
};