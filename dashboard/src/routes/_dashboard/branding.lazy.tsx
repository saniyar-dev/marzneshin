import { Page } from '@marzneshin/common/components'
import { BrandingWidget } from '@marzneshin/modules/settings'
import { createLazyFileRoute } from '@tanstack/react-router'
import { useTranslation } from 'react-i18next'

export const Branding = () => {
    const { t } = useTranslation()
    return (
        <Page title={t('branding')}>
            <BrandingWidget />
        </Page>
    )
}

export const Route = createLazyFileRoute('/_dashboard/branding')({
    component: Branding,
})