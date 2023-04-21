import { defineStore } from 'pinia'

export const useGlobalStore = defineStore('globalStore', {
    state: () => {
        return {
            fsmDef: undefined,
            chatfaqWS: {},
            chatfaqAPI: {},
            userId: undefined,
            title: "",
            subtitle: "",
            darkMode: false,
            menuOpened: false,
            maximized: true,
            historyOpened: true,
            conversations: [],
            selectedConversations: [],
            // The value of this property is irrelevant, what it really matters is the fact that its value changed,
            // which happens every time "New Conversation" button is clicked, then other components will subscribe
            // for any change and react to the fact that has been clicked
            newConversation: 0,
            opened: false,
            deleting: false,
            downloading: false
        }
    },
    actions: {
        async gatherConversations() {
            let response = await fetch(this.chatfaqAPI + `/back/api/broker/conversations?id=${this.userId}`);
            this.conversations = await response.json();
        },
    },
    getters: {
        conversationsIds() {
            return this.conversations.reduce((acc, current) => acc.concat([current[0]]), [])
        }
    }
})
