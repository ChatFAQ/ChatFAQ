import WidgetLoader from './WidgetLoader.vue';
import {createPinia} from 'pinia'
import PrimeVue from 'primevue/config'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Toast from 'primevue/toast'
import ToastService from 'primevue/toastservice'
import SelectButton from "primevue/selectbutton";
import TextArea from "primevue/textarea";

import { createApp } from 'vue'
function loadWidget(selector) {
    const el = document.querySelector(selector);
    createApp(
        WidgetLoader, { ...el.dataset }
    ).use(
        createPinia()
    ).use(
        PrimeVue, { ripple: true }
    ).use(
        ToastService
    ).component(
        'Button', Button
    ).component(
        'InputText', InputText
    ).component(
        'Toast', Toast
    ).component(
        'SelectButton', SelectButton
    ).component(
        'TextArea', TextArea
    ).use(
        createPinia()
    ).mount(selector);
}
export { loadWidget }
