import {
    createFileRoute,
    useNavigate,
} from "@tanstack/react-router";
import {
    useRouterUserContext,
    UsersSettingsDialog,
} from "@fishy/modules/users";
import { useDialog } from "@fishy/common/hooks";

const UserOpen = () => {
    const [settingsDialogOpen, setSettingsDialogOpen] = useDialog(true);
    const value = useRouterUserContext()
    const navigate = useNavigate({ from: "/users/$userId" });

    return value && (
        <UsersSettingsDialog
            open={settingsDialogOpen}
            onOpenChange={setSettingsDialogOpen}
            entity={value.user}
            isPending={!!value.isPending}
            onClose={() => navigate({ to: "/users" })}
        />
    );
}

export const Route = createFileRoute('/_dashboard/users/$userId/')({
    component: UserOpen
})
