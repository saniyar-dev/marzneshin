import { z } from "zod";
import { HostSchema, TlsSchema } from "@fishy/modules/hosts";

export const ShadowTlsSchema =
    HostSchema.merge(TlsSchema);

export type ShadowTlsSchemaType = z.infer<typeof ShadowTlsSchema>;
