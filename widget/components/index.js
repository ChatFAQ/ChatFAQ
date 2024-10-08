import Widget from "./Widget.vue";
import { createApp } from "vue";
import {_createI18n, _createPinia} from "../plugins";

function _buildApp(props) {
    return createApp(Widget, { ...props }).use(_createPinia()).use(_createI18n())
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
    connectedCallback() {
        const app = _buildApp(this.dataset);
        app.mount(this)
    }
}

export { ChatfaqWidgetCustomElement, ChatfaqWidget };
