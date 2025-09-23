import Widget from "./Widget.vue";
import { createApp, h } from "vue";
import {_createI18n, _createPinia} from "../plugins";
import { createHead } from '@unhead/vue/client'

let expose
function _buildApp(props) {
    const app = createApp({ render: () => expose = h(Widget, props) })
        .use(_createPinia())
        .use(_createI18n());
    app.use(createHead());
    return app;
}

class ChatfaqWidget {
    constructor(attrs) {
        if (typeof attrs.element == "string")
            attrs.element = document.querySelector(attrs.element)
        this.element = attrs.element;

        const props = { ...this.element.dataset, ...attrs }

        this.app = _buildApp(props);
    }

    mount() {
        this.app.mount(this.element)
    }
}

// couldn't implement this: https://rimdev.io/vue-3-custom-elements cause shadow dom problems (Rollup does not include 'styles' inside the .ce.vue element)
// a possible solution is to use Vite istead of Rollup as such: https://maximomussini.com/posts/vue-custom-elements
// for the moment we just implemented: https://github.com/vuejs/vue-web-component-wrapper/issues/93#issuecomment-909136116
class ChatfaqWidgetCustomElement extends HTMLElement {
    static get observedAttributes() {
        return ['data-split-screen-iframe']; // Add any other attributes you want to observe
    }

    connectedCallback() {
        this.app = _buildApp(this.dataset);
        this.app.mount(this)
    }

    attributeChangedCallback(name, oldValue, newValue) {
        if (!this.app) return; // Guard if app isn't mounted yet

        // Convert the attribute name to a prop name (remove 'data-' prefix and convert to camelCase)
        const propName = name.replace('data-', '')
            .replace(/-([a-z])/g, (g) => g[1].toUpperCase());

        // Update the prop in the Vue app
        window.testApp = this.app;
        expose.component.props[propName] = newValue;
    }
}
export { ChatfaqWidgetCustomElement, ChatfaqWidget };
