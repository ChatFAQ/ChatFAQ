import { createI18n } from "vue-i18n";
import en from '~/locales/en.json'
import fr from '~/locales/fr.json'
import es from '~/locales/es.json'
import {createPinia} from 'pinia'

export function _createPinia() {
    return createPinia();
}

export function _createI18n() {
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

export default {}
