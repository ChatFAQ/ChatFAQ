import {defineStore} from 'pinia'

export const useGlobalStore = defineStore('globalStore', {
    state: () => {
        return {
            fsmDef: undefined,
            chatfaqWS: {},
            chatfaqAPI: {},
            title: "",
            subtitle: "",
            darkMode: false,
            menuOpened: false,
            maximized: false,
        }
    },
})
