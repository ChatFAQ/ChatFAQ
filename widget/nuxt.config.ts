// https://nuxt.com/docs/api/configuration/nuxt-config

export default defineNuxtConfig({
    css: [
        'primevue/resources/themes/saga-blue/theme.css',
        'primevue/resources/primevue.css',
        'primeicons/primeicons.css',
        'primeflex/primeflex.css',
        '~/assets/styles/global.scss'
    ],
    build: {
        transpile: ['primevue']
    },
    runtimeConfig: {
        // The private keys which are only available server-side
        // privateKey: process.env.PRIVATE_KEY,
        // Keys within public are also exposed client-side
        public: {
            riddlerAPI: process.env.RIDDLER_API,
            riddlerWS: process.env.RIDDLER_WS,
        }
    },
    app: {
        head: {
            style: [
                {children: 'body { margin: 0 }'}
            ],
        }
    }
})