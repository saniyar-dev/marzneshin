import { type FC } from "react";
import { BooleanPill } from "@fishy/common/components";
import { useTranslation } from "react-i18next";
import { AdminProp } from "@fishy/modules/admins";

export const AdminEnabledPill: FC<AdminProp> = ({ admin }) => {
    const { t } = useTranslation();
    return (
        <BooleanPill
            active={admin.enabled}
            activeLabel={t('enabled')}
            inactiveLabel={t('disabled')}
        />
    )
}
