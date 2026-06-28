import { type FC } from "react";
import { BooleanPill } from "@fishy/common/components";
import { useTranslation } from "react-i18next";
import { UserProp } from "@fishy/modules/users";

export const UserActivatedPill: FC<UserProp> = ({ user }) => {
    const { t } = useTranslation();
    return (
        <BooleanPill
            active={user.activated}
            activeLabel={t('active')}
            inactiveLabel={t('inactive')}
        />
    )
}
