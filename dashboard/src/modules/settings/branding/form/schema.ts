import { z } from "zod";

export const schema = z.object({
    brand_shop_name: z
        .string()
        .max(64, "Shop name must be at most 64 characters")
        .nullable()
        .optional()
        .transform((v) => (v && v.trim().length > 0 ? v.trim() : null)),
    brand_support_url: z
        .string()
        .url("Support URL must be a valid URL")
        .max(512, "Support URL must be at most 512 characters")
        .or(z.literal(""))
        .nullable()
        .optional()
        .transform((v) => (v && v.length > 0 ? v : null)),
    brand_logo_filename: z.string().nullable().optional(),
});

export type Schema = z.infer<typeof schema>;