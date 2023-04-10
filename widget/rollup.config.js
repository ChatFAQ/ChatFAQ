import fs from "fs";
import path from "path";
import vue from "rollup-plugin-vue";
import alias from "@rollup/plugin-alias";
import commonjs from "@rollup/plugin-commonjs";
import resolve from "@rollup/plugin-node-resolve";
import replace from "@rollup/plugin-replace";
import {terser} from "rollup-plugin-terser";
import minimist from "minimist";
import babel from '@rollup/plugin-babel';
import styles from "rollup-plugin-styles";
import Components from 'unplugin-vue-components/rollup'
import json from '@rollup/plugin-json';

// Get browserslist config and remove ie from es build targets
const esbrowserslist = fs.readFileSync("./.browserslistrc")
    .toString()
    .split("\n")
    .filter((entry) => entry && entry.substring(0, 2) !== "ie");

// Extract babel preset-env config, to combine with esbrowserslist
const babelPresetEnvConfig = require("./babel.config")
    .presets.filter((entry) => entry[0] === "@babel/preset-env")[0][1];

const argv = minimist(process.argv.slice(2));

const projectRoot = path.resolve(__dirname);
const baseConfig = {
    input: "components/entry.js",
    plugins: {
        preVue: [
            alias({
                entries: [
                    {
                        find: "@",
                        replacement: `${path.resolve(projectRoot)}`,
                    },
                    {
                        find: "~",
                        replacement: `${path.resolve(projectRoot)}`,
                    },
                    {
                        find: "#build",
                        replacement: `.nuxt`,
                    },
                ],
            }),
            json()
        ],
        replace: {
            preventAssignment: true,
            "process.env.NODE_ENV": JSON.stringify("production"),
            "process.server": false,
            "process.client": true,
            "process.dev": false,
        },
        // scss: scss(),
        vue: {
            css: true, // Dynamically inject css as a <style> tag
            compileTemplate: true, // Explicitly convert template to render function
            template: {
                isProduction: true,
            },
            isWebComponent: true // Why is this not injecting the styles inside the component???
        },
        postVue: [
            resolve({
                extensions: [".js", ".jsx", ".ts", ".tsx", ".vue"],
            }),
            // Process only `<style module>` blocks.
            /*
            scss({
                include: ["assets/styles/*.scss"],
            }),
            */
            /*
            PostCSS({
                modules: {
                    generateScopedName: "[local]___[hash:base64:5]",
                },
                include: /&module=.*\.css$/,
            }),
            // Process all `<style>` blocks except `<style module>`.
            PostCSS({ include: /(?<!&module=.*)\.css$/ }),
            */
            // postcss({
            //     minimize: true,
            // }),
            styles({
                alias: {
                    "~": projectRoot
                }
            }),
            commonjs(),
            Components({
                "dirs": [`${path.resolve(projectRoot, "components")}`]
            })
        ],
        babel: {
            exclude: "node_modules/**",
            extensions: [".js", ".jsx", ".ts", ".tsx", ".vue"],
            babelHelpers: "bundled",
        },
    },
};

// ESM/UMD/IIFE shared settings: externals
// Refer to https://rollupjs.org/guide/en/#warning-treating-module-as-external-dependency
const external = [
    // list external dependencies, exactly the way it is written in the import statement.
    // eg. 'jquery'
    "vue",
];

// UMD/IIFE shared settings: output.globals
// Refer to https://rollupjs.org/guide/en#output-globals for details
const globals = {
    // Provide global variable names to replace your external imports
    // eg. jquery: '$'
    vue: "Vue",
};

// Customize configs for individual targets
const buildFormats = [];
if (!argv.format || argv.format === "es") {
    const esConfig = {
        ...baseConfig,
        input: "components/entry.esm.js",
        external,
        output: {
            file: "dist/widget.esm.js",
            format: "esm",
            exports: "named",
        },
        plugins: [
            replace(baseConfig.plugins.replace),
            ...baseConfig.plugins.preVue,
            vue(baseConfig.plugins.vue),
            ...baseConfig.plugins.postVue,
            babel({
                ...baseConfig.plugins.babel,
                presets: [
                    [
                        "@babel/preset-env",
                        {
                            ...babelPresetEnvConfig,
                            targets: esbrowserslist,
                        },
                    ],
                ],
            }),
        ],
    };
    buildFormats.push(esConfig);
}

if (!argv.format || argv.format === "cjs") {
    const umdConfig = {
        ...baseConfig,
        external,
        output: {
            compact: true,
            file: "dist/widget.ssr.js",
            format: "cjs",
            name: "Widget",
            exports: "auto",
            globals,
        },
        plugins: [
            replace(baseConfig.plugins.replace),
            ...baseConfig.plugins.preVue,
            vue(baseConfig.plugins.vue),
            ...baseConfig.plugins.postVue,
            babel(baseConfig.plugins.babel),
        ],
    };
    buildFormats.push(umdConfig);
}

if (!argv.format || argv.format === "iife") {
    const unpkgConfig = {
        ...baseConfig,
        external,
        output: {
            compact: true,
            file: "dist/widget.min.js",
            format: "iife",
            name: "Widget",
            exports: "auto",
            globals,
        },
        plugins: [
            replace(baseConfig.plugins.replace),
            ...baseConfig.plugins.preVue,
            vue(baseConfig.plugins.vue),
            ...baseConfig.plugins.postVue,
            babel(baseConfig.plugins.babel),
            terser({
                output: {
                    ecma: 5,
                },
            }),
        ],
    };
    buildFormats.push(unpkgConfig);
}

// Export config
export default buildFormats;
