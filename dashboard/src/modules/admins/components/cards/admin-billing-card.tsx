import { format } from "@chbphone55/pretty-bytes";
import { useTranslation } from "react-i18next";
import { FC } from "react";
import { Gauge, ReceiptText } from "lucide-react";

import {
    Button,
    Card,
    CardContent,
    CardHeader,
    CardTitle,
    Skeleton,
    Table,
    TableBody,
    TableRowWithCell,
} from "@fishy/common/components";
import {
    useAdminBillingQuery,
    useSetAdminBillingCheckpointMutation,
} from "@fishy/modules/admins";

interface AdminBillingCardProps {
    username: string | null;
    allowCheckpoint?: boolean;
}

const SkeletonRows: FC = () => (
    <Card>
        <CardHeader>
            <CardTitle>
                <Skeleton className="w-32 h-6" />
            </CardTitle>
        </CardHeader>
        <CardContent>
            <Skeleton className="w-full h-32" />
        </CardContent>
    </Card>
);

const formatBytes = (n: number | null | undefined): string => {
    if (n === null || n === undefined) return "-";
    const [value, unit] = format(n);
    return `${value} ${unit}`;
};

export const AdminBillingCard: FC<AdminBillingCardProps> = ({
    username,
    allowCheckpoint = false,
}) => {
    const { t } = useTranslation();
    const { data, isPending } = useAdminBillingQuery({ username });
    const { mutate: setCheckpoint, isPending: settingCheckpoint } =
        useSetAdminBillingCheckpointMutation();

    if (isPending || !data) return <SkeletonRows />;

    return (
        <Card>
            <CardHeader className="flex flex-row justify-between items-center w-full">
                <CardTitle className="flex gap-2 items-center">
                    <ReceiptText className="w-5 h-5" />
                    {t("page.admins.billing.title")}
                </CardTitle>
                {allowCheckpoint && (
                    <Button
                        size="sm"
                        className="bg-success rounded-2xl"
                        disabled={settingCheckpoint}
                        onClick={() =>
                            setCheckpoint({
                                username: data.username,
                                note: `checkpoint at ${new Date().toISOString()}`,
                            })
                        }
                    >
                        <Gauge className="mr-2 w-4 h-4" />
                        {t("page.admins.billing.set_checkpoint")}
                    </Button>
                )}
            </CardHeader>
            <CardContent>
                <Table>
                    <TableBody>
                        <TableRowWithCell
                            label={t(
                                "page.admins.billing.total_billable_bytes",
                            )}
                            value={formatBytes(data.total_billable_bytes)}
                        />
                        <TableRowWithCell
                            label={t("page.admins.billing.unbilled_bytes")}
                            value={formatBytes(data.unbilled_bytes)}
                        />
                        <TableRowWithCell
                            label={t(
                                "page.admins.billing.last_checkpoint_bytes",
                            )}
                            value={formatBytes(data.last_checkpoint_bytes)}
                        />
                        <TableRowWithCell
                            label={t(
                                "page.admins.billing.last_checkpoint_at",
                            )}
                            value={
                                data.last_checkpoint_at
                                    ? new Date(
                                          data.last_checkpoint_at,
                                      ).toLocaleString()
                                    : "-"
                            }
                        />
                        <TableRowWithCell
                            label={t("page.admins.billing.event_count")}
                            value={String(data.event_count)}
                        />
                    </TableBody>
                </Table>
            </CardContent>
        </Card>
    );
};

export const AdminBillingCardForCurrent: FC = () => (
    <AdminBillingCard username={null} allowCheckpoint={false} />
);

export const AdminBillingCardForAdmin: FC<{ username: string }> = ({
    username,
}) => <AdminBillingCard username={username} allowCheckpoint />;
