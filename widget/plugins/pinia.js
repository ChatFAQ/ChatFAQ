import {_createPinia} from "./index";

export default defineNuxtPlugin(nuxtApp => {
    nuxtApp.vueApp.use(_createPinia())
})
