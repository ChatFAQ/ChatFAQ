// https://nuxt.com/docs/api/configuration/nuxt-config
import dns from "dns";

dns.setDefaultResultOrder('ipv4first')
import {resolve, dirname} from 'node:path'
import {fileURLToPath} from 'url'
import VueI18nVitePlugin from '@intlify/unplugin-vue-i18n/vite'


export default defineNuxtConfig({
    ssr: true,
    build: {
        transpile: []
    },
    devServer: {
        port: parseInt(process.env.WIDGET_PORT ?? "3000"),
    },
    runtimeConfig: {
        // The private keys which are only available server-side
        // privateKey: process.env.PRIVATE_KEY,
        // Keys within public are also exposed client-side

        // In order to pass env variables to the client AT RUNTIME, you have to
        // use a specially named env variable:
        // use the prefix NUXT_ to override defaults, and _ to split capitalization:
        //  - for private runtime variables (server only), just NUXT_VARNAME
        //  - for public runtime variables (both), use NUXT_PUBLIC_VARNAME
        // these 2 can be set at runtime by defining the vars NUXT_PUBLIC_CHATFAQ_BACKEND_API and NUXT_PUBLIC_CHATFAQ_BACKEND_WS
        public: {
            chatfaqAPI: (process.env.NUXT_PUBLIC_CHATFAQ_API || process.env.CHATFAQ_API) ?? "",
            chatfaqWS: (process.env.NUXT_PUBLIC_CHATFAQ_WS || process.env.CHATFAQ_WS) ?? "",
            SENTRY_DNS: (process.env.SENTRY_DNS) ?? "",
        }
    },
    app: {
        baseURL: "/demo",
        head: {
            style: [
                {children: 'body { margin: 0 }'}
            ],
        }
    },
    vite: {
        plugins: [
            VueI18nVitePlugin({
                include: [
                    resolve(dirname(fileURLToPath(import.meta.url)), './locales/*.json')
                ]
            })
        ],
        css: {
            preprocessorOptions: {
                scss: {
                    additionalData: `@import "~/assets/styles/global.scss";`,
                },
            },
        }
    },
    modules: ["@sentry/nuxt/module"],
})
