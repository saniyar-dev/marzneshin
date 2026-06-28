import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
    DropdownMenuGroup,
    Button,
} from "@fishy/common/components";
import { Link } from "@tanstack/react-router";
import { FC } from 'react';
import { Settings, MenuIcon, Paintbrush, ShieldCheck } from "lucide-react";
import { LanguageSwitchMenu } from "@fishy/features/language-switch";
import { ThemeToggle } from "@fishy/features/theme-switch";
import { useAuth, Logout } from "@fishy/modules/auth";
import { useScreenBreakpoint } from "@fishy/common/hooks/use-screen-breakpoint";
import { useTranslation } from "react-i18next";
import { VersionIndicator } from "@fishy/features/version-indicator";

export const HeaderMenu: FC = () => {

    const isDesktop = useScreenBreakpoint("md");
    const { isSudo } = useAuth();
    const { t } = useTranslation();

    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button
                    variant="secondary"
                    className="bg-gray-800 text-secondary dark:hover:bg-secondary-foreground dark:hover:text-secondary dark:text-secondary-foreground"
                    size="icon"
                >
                    <MenuIcon />
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
                <DropdownMenuLabel>Menu</DropdownMenuLabel>
                <DropdownMenuSeparator />
                {(!isDesktop && isSudo()) && (
                    <>
                        <DropdownMenuItem className="w-full">
                            <Link to="/settings" className="hstack gap-1 items-center justify-between w-full h-fit p-0">
                                {t("settings")}
                                <Settings className="size-4" />
                            </Link>
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem className="w-full">
                            <Link to="/admins" className="hstack gap-1 items-center justify-between w-full h-fit p-0" >
                                {t("admins")}
                                <ShieldCheck className="size-4" />
                            </Link>
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                    </>
                )}
                {!isDesktop && (
                    <DropdownMenuItem className="w-full">
                        <Link to="/branding" className="hstack gap-1 items-center justify-between w-full h-fit p-0">
                            {t("branding")}
                            <Paintbrush className="size-4" />
                        </Link>
                    </DropdownMenuItem>
                )}
                <DropdownMenuItem className="w-full">
                    <Logout />
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuGroup>
                    <LanguageSwitchMenu />
                    <ThemeToggle />
                </DropdownMenuGroup>
                <DropdownMenuSeparator />
                <DropdownMenuGroup className="py-1 shrink-0">
                    <VersionIndicator />
                </DropdownMenuGroup>
            </DropdownMenuContent>
        </DropdownMenu >
    )
};
