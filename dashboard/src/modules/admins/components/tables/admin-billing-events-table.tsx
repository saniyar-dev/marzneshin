import { format } from "@chbphone55/pretty-bytes";
import { useTranslation } from "react-i18next";
import { FC } from "react";

import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
    Skeleton,
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
    ScrollArea,
} from "@fishy/common/components";
import {
    AdminBillingEventKind,
    AdminBillingEventType,
    useAdminBillingEventsQuery,
} from "@fishy/modules/admins";

interface AdminBillingEventsTableProps {
    username: string | null;
    eventType?: AdminBillingEventKind;
    limit?: number;
}

export const AdminBillingEventsTable: FC<AdminBillingEventsTableProps> = ({
    username,
    eventType,
    limit = 100,
}) => {
    const { t } = useTranslation();
    const { data, isPending } = useAdminBillingEventsQuery({
        username,
        eventType,
        limit,
    });

    if (isPending) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle>
                        <Skeleton className="w-40 h-6" />
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <Skeleton className="w-full h-64" />
                </CardContent>
            </Card>
        );
    }

    const events = data ?? [];

    return (
        <Card>
            <CardHeader>
                <CardTitle>{t("page.admins.billing.events_title")}</CardTitle>
            </CardHeader>
            <CardContent>
                <ScrollArea className="w-full">
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>
                                    {t("page.admins.billing.event_type")}
                                </TableHead>
                                <TableHead>
                                    {t("page.admins.billing.event_user")}
                                </TableHead>
                                <TableHead>
                                    {t("page.admins.billing.event_amount")}
                                </TableHead>
                                <TableHead>
                                    {t("page.admins.billing.event_occurred_at")}
                                </TableHead>
                                <TableHead>
                                    {t("note")}
                                </TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {events.length === 0 ? (
                                <TableRow>
                                    <TableCell colSpan={5} className="text-center text-muted-foreground">
                                        {t("page.admins.billing.no_events")}
                                    </TableCell>
                                </TableRow>
                            ) : (
                                events.map((e: AdminBillingEventType) => {
                                    const [value, unit] = format(e.bytes_amount);
                                    return (
                                        <TableRow key={e.id}>
                                            <TableCell>
                                                {t(
                                                    `page.admins.billing.event_kinds.${e.event_type}`,
                                                )}
                                            </TableCell>
                                            <TableCell>{e.user_id}</TableCell>
                                            <TableCell>
                                                {value} {unit}
                                            </TableCell>
                                            <TableCell>
                                                {new Date(
                                                    e.occurred_at,
                                                ).toLocaleString()}
                                            </TableCell>
                                            <TableCell className="text-muted-foreground">
                                                {e.note ?? "-"}
                                            </TableCell>
                                        </TableRow>
                                    );
                                })
                            )}
                        </TableBody>
                    </Table>
                </ScrollArea>
            </CardContent>
        </Card>
    );
};