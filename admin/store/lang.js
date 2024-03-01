import {defineStore} from 'pinia';

export const useLangStore = defineStore('lang', {
    state: () => ({
        lang: useCookie('lang').value || 'en'
    }),
    actions: {
        setLang(lang) {
            useCookie('lang').value = lang;
            this.lang = lang;
        }
    }
});
