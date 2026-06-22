import {
    FormItem,
    FormLabel,
    FormControl,
    Button,
} from "@marzneshin/common/components";
import { useFormContext, useWatch, useController } from "react-hook-form";
import { useTranslation } from "react-i18next";
import { useLogoUploadMutation } from "@marzneshin/modules/settings/branding";
import { Trash2, Upload, Image as ImageIcon } from "lucide-react";
import { useRef } from "react";
import type { Schema } from "../schema";

const ALLOWED_TYPES = "image/png,image/jpeg,image/webp,image/svg+xml";
const ALLOWED_EXTS = ".png,.jpg,.jpeg,.webp,.svg";

const logoUrl = (filename: string) => `/brand-logos/${filename}`;

export const LogoUploadField = () => {
    const { t } = useTranslation();
    const { control, setValue } = useFormContext<Schema>();
    const inputRef = useRef<HTMLInputElement>(null);
    const { field } = useController({ control, name: "brand_logo_filename" });
    const upload = useLogoUploadMutation();

    const currentFilename = useWatch({ control, name: "brand_logo_filename" });

    const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        e.target.value = "";
        if (!file) return;
        upload.mutate(file, {
            onSuccess: (res) => {
                field.onChange(res.filename);
            },
        });
    };

    const handleRemove = () => {
        setValue("brand_logo_filename", null, { shouldDirty: true });
    };

    return (
        <FormItem>
            <FormLabel>{t("page.branding.logo")}</FormLabel>
            <FormControl>
                <div className="flex flex-col gap-3">
                    {currentFilename ? (
                        <div className="flex items-center gap-3">
                            <img
                                src={logoUrl(currentFilename)}
                                alt={t("page.branding.logo")}
                                className="h-16 w-auto max-w-[160px] rounded border bg-white p-1 object-contain"
                            />
                            <Button
                                type="button"
                                variant="ghost"
                                size="sm"
                                onClick={handleRemove}
                                className="text-destructive"
                            >
                                <Trash2 className="size-4" />
                                {t("page.branding.remove")}
                            </Button>
                        </div>
                    ) : (
                        <div className="flex h-16 w-full items-center justify-center rounded border border-dashed text-sm text-muted-foreground">
                            <ImageIcon className="mr-2 size-4" />
                            {t("page.branding.no-logo")}
                        </div>
                    )}
                    <div>
                        <input
                            ref={inputRef}
                            type="file"
                            accept={ALLOWED_TYPES}
                            onChange={handleFile}
                            disabled={upload.isPending}
                            className="hidden"
                        />
                        <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={() => inputRef.current?.click()}
                            disabled={upload.isPending}
                        >
                            <Upload className="size-4" />
                            {upload.isPending
                                ? t("page.branding.uploading")
                                : currentFilename
                                    ? t("page.branding.replace")
                                    : t("page.branding.upload")}
                        </Button>
                        <p className="mt-1 text-xs text-muted-foreground">
                            {t("page.branding.logo-hint", { exts: ALLOWED_EXTS })}
                        </p>
                    </div>
                </div>
            </FormControl>
        </FormItem>
    );
};