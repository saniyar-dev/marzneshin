import {
    FormField,
    FormItem,
    FormLabel,
    FormControl,
    FormMessage,
    Input,
} from "@marzneshin/common/components";
import { useFormContext } from "react-hook-form";
import { useTranslation } from "react-i18next";

export const ShopNameField = () => {
    const { t } = useTranslation();
    const form = useFormContext();
    return (
        <FormField
            control={form.control}
            name="brand_shop_name"
            render={({ field }) => (
                <FormItem>
                    <FormLabel>
                        {t("page.branding.shop-name")}
                    </FormLabel>
                    <FormControl>
                        <Input
                            className="h-8"
                            placeholder={t("page.branding.shop-name-placeholder")}
                            {...field}
                            value={field.value ?? ""}
                            onChange={(e) =>
                                field.onChange(
                                    e.target.value === ""
                                        ? null
                                        : e.target.value,
                                )
                            }
                        />
                    </FormControl>
                    <FormMessage />
                </FormItem>
            )}
        />
    );
};