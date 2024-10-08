import { envManager, defineModelWConfig } from "@model-w/preset-nuxt3";
import { defu } from "defu";

const fs = require('fs')
const packageJson = fs.readFileSync('./package.json')
const widgetVersion = JSON.parse(packageJson)["dependencies"]["chatfaq-widget"] || 0


export default envManager((env) => {
    const config = defineModelWConfig(env, {
        siteName: "ChatFAQ Admin",
        head: {
            title: "ChatFAQ Admin",
            meta: [
                { charset: "utf-8" },
                {
                    name: "viewport",
                    content: "width=device-width, initial-scale=1",
                },
                { name: "format-detection", content: "telephone=no" },
            ],
        },
    });
    const viteNuxtConfig = defineNuxtConfig({
        ssr: true,
        css: ["@/assets/styles/global.scss"],
        buildModules: [],
        modules: [...config.modules, "@pinia/nuxt", "@element-plus/nuxt"],
        vite: {
            css: {
                preprocessorOptions: {
                    scss: {
                        additionalData: `
                            @import "@/assets/styles/settings/settings.colors.scss";
                            @import "@/assets/styles/settings/settings.global.scss";
                            @import "@/assets/styles/reusable/breakpoints.scss";
                            @import "@/assets/styles/mixins.scss";
                        `,
                    },
                },
            },
        },
        // app: { baseURL: process.env.BASE_URL || "/" },
        runtimeConfig: {
            public: {
                chatfaqWS: (process.env.NUXT_PUBLIC_CHATFAQ_WS || process.env.CHATFAQ_WS) ?? "",
                widgetVersion: widgetVersion,
            },
        },
        vue: {
            compilerOptions: {
                isCustomElement: (tag) => ['chatfaq-widget'].includes(tag),
            },
        },
        i18n: {
            locales: ['en', 'es', 'fr'],
            defaultLocale: 'en'
        }
    });

    const out = defu(config, viteNuxtConfig);
    delete out.app.head.titleTemplate;

    return out;
});
