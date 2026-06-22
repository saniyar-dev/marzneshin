import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { useTranslation } from "react-i18next";
import {
    Button,
    Form,
    HStack,
} from "@marzneshin/common/components";
import { useCurrentAdminQuery } from "@marzneshin/modules/admins";
import {
    useBrandingMutation,
} from "@marzneshin/modules/settings/branding";
import { useEffect } from "react";
import { schema, Schema } from "./schema";
import {
    ShopNameField,
    SupportUrlField,
    LogoUploadField,
} from "./fields";

const DEFAULTS: Schema = {
    brand_shop_name: null,
    brand_support_url: null,
    brand_logo_filename: null,
};

export function BrandingForm() {
    const { t } = useTranslation();
    const { data, isFetching } = useCurrentAdminQuery();
    const mutate = useBrandingMutation();

    const form = useForm<Schema>({
        resolver: zodResolver(schema),
        defaultValues: DEFAULTS,
    });

    useEffect(() => {
        if (data) {
            form.reset(
                {
                    brand_shop_name: data.brand_shop_name ?? null,
                    brand_support_url: data.brand_support_url ?? null,
                    brand_logo_filename: data.brand_logo_filename ?? null,
                },
                { keepDirtyValues: true },
            );
        }
    }, [data, form]);

    const onSubmit = (values: Schema) => {
        mutate.mutate({
            brand_shop_name: values.brand_shop_name,
            brand_support_url: values.brand_support_url,
            brand_logo_filename: values.brand_logo_filename,
        });
    };

    return (
        <Form {...form}>
            <form
                onSubmit={form.handleSubmit(onSubmit)}
                className="flex w-full max-w-4xl flex-col gap-2"
            >
                <ShopNameField />
                <SupportUrlField />
                <LogoUploadField />
                <HStack className="w-full flex-end mt-2">
                    <Button
                        type="button"
                        variant="destructive"
                        className="w-fit"
                        onClick={() => form.reset(DEFAULTS)}
                        disabled={isFetching}
                    >
                        {t("page.settings.subscription-settings.reset-local-changes")}
                    </Button>
                    <Button
                        type="submit"
                        className="w-fit"
                        disabled={mutate.isPending}
                    >
                        {t("submit")}
                    </Button>
                </HStack>
            </form>
        </Form>
    );
}