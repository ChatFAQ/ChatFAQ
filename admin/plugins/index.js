import { createI18n } from "vue-i18n";
import en from '~/locales/en.json'
export function _createI18n() {
    return createI18n({
        legacy: false,
        globalInjection: true,
        locale: "en",
        messages: {
            en,
        },
    });
}

export default {}
