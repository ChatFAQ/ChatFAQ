import {defineStore} from 'pinia'

export const useGlobalStore = defineStore('fsmDef', {
    state: () => {
        return {
            selectedFSMDef: {},
            chatfaqWS: {},
            chatfaqAPI: {}
        }
    },
})
