import {defineStore} from 'pinia'

export const useFSMDef = defineStore('fsmDef', {
    state: () => {
        return {selectedFSMDef: {}}
    },
})
