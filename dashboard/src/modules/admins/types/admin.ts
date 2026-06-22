
export interface AdminType {
    id: number;
    username: string;
    enabled: boolean;
    is_sudo: boolean;
    all_services_access: boolean;
    modify_users_access: boolean;
    service_ids: number[];
    subscription_url_prefix: string;
    users_data_usage: number;
    brand_shop_name: string | null;
    brand_logo_filename: string | null;
    brand_support_url: string | null;
}

