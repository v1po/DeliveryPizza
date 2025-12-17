/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_AUTH_SERVICE_URL: string
  readonly VITE_CATALOG_SERVICE_URL: string
  readonly VITE_ORDER_SERVICE_URL: string
  readonly VITE_GATEWAY_URL: string
  readonly VITE_ACCESS_TOKEN_KEY: string
  readonly VITE_REFRESH_TOKEN_KEY: string
  readonly VITE_API_TIMEOUT: string
  readonly VITE_APP_NAME: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}