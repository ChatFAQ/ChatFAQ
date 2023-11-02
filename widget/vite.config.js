// vite.config.js
import path, { resolve } from "path";
import { defineConfig, loadEnv } from "vite";
import vue from "@vitejs/plugin-vue";
import cssInjectedByJsPlugin from "vite-plugin-css-injected-by-js";


export default ({ mode }) => {
    const env = loadEnv(mode, process.cwd(), "");

    return defineConfig({

        define: {
            "process.env": env,
        },
        plugins: [vue(), cssInjectedByJsPlugin()],
        resolve: {
            alias: {
                "@": path.resolve(__dirname),
                "~": path.resolve(__dirname),
            },
        },
        css: {
            preprocessorOptions: {
                scss: {
                    additionalData: `@import "~/assets/styles/global.scss";`,
                },
            },
        },
        build: {
            lib: {
                // src/indext.ts is where we have exported the component(s)
                entry: resolve(__dirname, "components/index.js"),
                name: "ChatFAQWidget",
                // the name of the output files when the build is run
                fileName: "chatfaq-widget",
            },
            rollupOptions: {
                // make sure to externalize deps that shouldn't be bundled
                // into your library
                external: [],
                output: {
                    // Provide global variables to use in the UMD build
                    // for externalized deps
                    globals: {
                        vue: "Vue",
                    },
                },
            },
        },
    });
};
