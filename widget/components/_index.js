import WidgetLoader from "./WidgetLoader.ce.vue";
import { createPinia } from "pinia";
import PrimeVue from "primevue/config";
import Button from "primevue/button";
import InputText from "primevue/inputtext";
import Toast from "primevue/toast";
import ToastService from "primevue/toastservice";
import SelectButton from "primevue/selectbutton";
import TextArea from "primevue/textarea";

import { createApp, defineCustomElement, getCurrentInstance, h } from "vue";

function buildApp(el) {
    createApp(WidgetLoader, { ...el.dataset })
        .use(PrimeVue, { ripple: true })
        .use(ToastService)
        .use(createPinia())
        .component("Button", Button)
        .component("InputText", InputText)
        .component("Toast", Toast)
        .component("SelectButton", SelectButton)
        .component("TextArea", TextArea)
        .mount(el);
}

function loadWidget(selector) {
    const el = document.querySelector(selector);
    buildApp(el)
}

function createCustomElement() {
    /*
    const appAsElement = defineCustomElement({
        setup() {
            const app = createApp(WidgetLoader)
            .use(PrimeVue, { ripple: true })
            .use(ToastService)
            .use(createPinia())
            .component("Button", Button)
            .component("InputText", InputText)
            .component("Toast", Toast)
            .component("SelectButton", SelectButton)
            .component("TextArea", TextArea);

            // Copy context to this
            const inst = getCurrentInstance();
            Object.assign(inst.appContext, app._context);
            Object.assign(inst.provides, app._context.provides);
        },
        render: () => h(WidgetLoader),
    });
    */

    class ChatfaqWidgetCustomElement extends HTMLElement {
        connectedCallback() {
            buildApp(this)
        }
    }

    customElements.define("chatfaq-widget", MyChatApp);
}
// couldn't implement this: https://rimdev.io/vue-3-custom-elements cause shadow dom problems (Rollup does not include 'styles' inside the .ce.vue element)
// a possible solution is to use Vite istead of Rollup as such: https://maximomussini.com/posts/vue-custom-elements
// for the moment we just implemented: https://github.com/vuejs/vue-web-component-wrapper/issues/93#issuecomment-909136116
class ChatfaqWidgetCustomElement extends HTMLElement {
    connectedCallback() {
        buildApp(this)
    }
}

export { ChatfaqWidgetCustomElement, loadWidget };
