
import { FC } from "react";
import { DoubleEntityTable } from "@fishy/libs/entity-table";
import { columns } from "./columns";
import { fetchServiceUsers, type ServiceType } from "@fishy/modules/services";

interface ServicesUsersTableProps {
    service: ServiceType
}

export const ServicesUsersTable: FC<ServicesUsersTableProps> = ({ service }) => {

    return (
        <DoubleEntityTable
            columns={columns}
            entityId={service.id}
            fetchEntity={fetchServiceUsers}
            primaryFilter="username"
            entityKey='services'
        />
    )
}
