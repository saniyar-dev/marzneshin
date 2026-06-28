import {
    createFileRoute,
    useNavigate,
} from "@tanstack/react-router";
import {
    useRouterNodeContext,
    NodesSettingsDialog,
} from "@fishy/modules/nodes";
import { useDialog } from "@fishy/common/hooks";

const NodeOpen = () => {
    const [settingsDialogOpen, setSettingsDialogOpen] = useDialog(true);
    const value = useRouterNodeContext()
    const navigate = useNavigate({ from: "/nodes/$nodeId" });

    return value && (
        <NodesSettingsDialog
            open={settingsDialogOpen}
            onOpenChange={setSettingsDialogOpen}
            entity={value.node}
            onClose={() => navigate({ to: "/nodes" })}
        />
    );
}

export const Route = createFileRoute('/_dashboard/nodes/$nodeId/')({
    component: NodeOpen
})
