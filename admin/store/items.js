import {defineStore} from 'pinia';

export const useItemsStore = defineStore('items', {
    state: () => ({
        items: {}
    }),
    actions: {
        async retrieveItems($axios, itemType) {
            this.items[itemType] = (await $axios.get(`/api/language-model/${itemType}/`)).data
        }
    }
});
