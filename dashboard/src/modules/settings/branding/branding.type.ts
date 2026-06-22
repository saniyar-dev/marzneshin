export interface BrandingType {
    brand_shop_name: string | null;
    brand_logo_filename: string | null;
    brand_support_url: string | null;
}

export interface LogoUploadResponse {
    filename: string;
    url: string;
}