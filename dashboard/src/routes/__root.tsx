import { TooltipProvider, Loading } from '@fishy/common/components';
import { ThemeProvider } from '@fishy/features/theme-switch'
import { queryClient } from '@fishy/common/utils';
import { QueryClientProvider } from '@tanstack/react-query';
import { createRootRoute, Outlet } from '@tanstack/react-router'
import { Suspense } from 'react'

export const Route = createRootRoute({
    component: () => (
        <QueryClientProvider client={queryClient}>
            <ThemeProvider defaultTheme="light" storageKey="ui-theme">
                <TooltipProvider>
                    <Suspense fallback={<Loading />}>
                        <Outlet />
                    </Suspense>
                </TooltipProvider>
            </ThemeProvider>
        </QueryClientProvider>
    ),
})
