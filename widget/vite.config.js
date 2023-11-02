// vite.config.js
import path, {resolve} from "path";
import {defineConfig, loadEnv} from "vite";
import vue from "@vitejs/plugin-vue";
import cssInjectedByJsPlugin from "vite-plugin-css-injected-by-js";

const stripScssMarker = '/* STYLES STRIP IMPORTS MARKER */'
const projectRootDir = path.resolve(__dirname)
export default ({mode}) => {
    const env = loadEnv(mode, process.cwd(), "");

    return defineConfig({
        root: "./",
        publicDir: "public",
        define: {
            "process.env": env,
        },
        plugins: [vue(), {
            name: 'vite-plugin-strip-css',
            transform(src, id) {
                if (id.endsWith('.vue') && !id.includes('node_modules') && src.includes('@extend')) {
                    console.warn(
                        'You are using @extend in your component. This is likely not working in your styles. Please use mixins instead.',
                        id.replace(`${projectRootDir}/`, '')
                    )
                }
                if (id.includes('lang.scss')) {
                    const split = src.split(stripScssMarker)
                    const newSrc = split[split.length - 1]

                    return {
                        code: newSrc,
                        map: null
                    }
                }
            }
        }, cssInjectedByJsPlugin()],
        resolve: {
            alias: {
                "@": projectRootDir,
                "~": projectRootDir,
            },
        },
        css: {
            preprocessorOptions: {
                scss: {
                    additionalData: `@import "${projectRootDir}/assets/styles/global.scss";${stripScssMarker}`
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
