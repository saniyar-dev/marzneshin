import {
    FormField,
    FormItem,
    FormLabel,
    FormControl,
    FormMessage,
    Input,
} from "@fishy/common/components";
import { useFormContext } from "react-hook-form";
import { useTranslation } from "react-i18next";

export const SupportUrlField = () => {
    const { t } = useTranslation();
    const form = useFormContext();
    return (
        <FormField
            control={form.control}
            name="brand_support_url"
            render={({ field }) => (
                <FormItem>
                    <FormLabel>
                        {t("page.branding.support-url")}
                    </FormLabel>
                    <FormControl>
                        <Input
                            className="h-8"
                            type="url"
                            placeholder="https://t.me/your_support"
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