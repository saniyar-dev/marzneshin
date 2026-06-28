import { HostWithProfileSchemaType } from "@fishy/modules/hosts";

export interface HostRequestDto {
    inboundId: number
    host: HostWithProfileSchemaType
}

export interface HostUpdateRequestDto {
    hostId: number
    host: HostWithProfileSchemaType
}
