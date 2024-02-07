import {_createI18n} from "./index";

export default defineNuxtPlugin(({ vueApp }) => {
    const i18n = _createI18n();

    vueApp.use(i18n);
});
