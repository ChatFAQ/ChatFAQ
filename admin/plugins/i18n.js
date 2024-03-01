import { createI18n } from "vue-i18n";
import en from '~/locales/en.json'
import es from '~/locales/es.json'
import fr from '~/locales/fr.json'
function _createI18n() {
    return createI18n({
        legacy: false,
        globalInjection: true,
        locale: "en",
        messages: {
            en,
            es,
            fr,
        },
    });
}

export default defineNuxtPlugin(({ vueApp }) => {
    const i18n = _createI18n();

    vueApp.use(i18n);
});
