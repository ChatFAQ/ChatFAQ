import { defineNuxtPlugin } from "nuxt/app";

import { ChatfaqWidgetCustomElement } from "chatfaq-widget";

export default defineNuxtPlugin(() => {
    customElements.define("chatfaq-widget", ChatfaqWidgetCustomElement);
});
