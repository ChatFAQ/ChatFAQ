import WidgetLoader from "./WidgetLoader.ce.vue";
import { createPinia } from "pinia";
import PrimeVue from "primevue/config";
import Button from "primevue/button";
import InputText from "primevue/inputtext";
import Toast from "primevue/toast";
import ToastService from "primevue/toastservice";
import SelectButton from "primevue/selectbutton";
import TextArea from "primevue/textarea";

import { createApp } from "vue";

function _buildApp(props) {
    return createApp(WidgetLoader, { ...props })
        .use(PrimeVue, { ripple: true })
        .use(ToastService)
        .use(createPinia())
        .component("Button", Button)
        .component("InputText", InputText)
        .component("Toast", Toast)
        .component("SelectButton", SelectButton)
        .component("TextArea", TextArea)
}

class ChatfaqWidget {
    constructor(element) {
        if (typeof element == "string")
            element = document.querySelector(element)
        this.element = element;
        this.app = _buildApp(element.dataset);
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
