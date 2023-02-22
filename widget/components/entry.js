// iife/cjs usage extends esm default export - so import it all
import plugin, * as components from "~/components/entry.esm";

// Attach named exports directly to plugin. IIFE/CJS will
// only expose one global var, with component exports exposed as properties of
// that global var (eg. plugin.component)
Object.entries(components).forEach(([componentName, component]) => {
    if (componentName !== "default") {
        plugin[componentName] = component;
    }
});

export default plugin;

/*
// Import vue component
import WidgetLoader from './WidgetLoader.ce.vue';

// Declare install function executed by Vue.use()
export function install(Vue) {
    if (install.installed) return;
    install.installed = true;
    Vue.component('WidgetLoader', WidgetLoader);
}

// Create module definition for Vue.use()
const plugin = {
    install,
};

// Auto-install when vue is found (eg. in browser via <script> tag)
let GlobalVue = null;
if (typeof window !== 'undefined') {
    GlobalVue = window.Vue;
} else if (typeof global !== 'undefined') {
    GlobalVue = global.Vue;
}
if (GlobalVue) {
    GlobalVue.use(plugin);
}

// To allow use as module (npm/webpack/etc.) export component
export default WidgetLoader;
*/
