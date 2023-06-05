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
            messages: [],
            selectedConversations: [],
            // The value of this properties (newConversation, scrollToBottom) is irrelevant, what it really matters is
            // the fact that its value changed, which happens every time "New Conversation" button is clicked, then
            // other components will subscribe for any change and react to the fact that has been clicked
            newConversation: 0,
            scrollToBottom: 0,
            opened: false,
            deleting: false,
            downloading: false
        }
    },
    actions: {
        async gatherConversations() {
            let response = await fetch(this.chatfaqAPI + `/back/api/broker/conversations/?sender=${this.userId}`);
            this.conversations = await response.json();
        },
        async renameConversationName(id, name) {
            await fetch(this.chatfaqAPI + `/back/api/broker/conversations/${id}/`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: name })
            });
            this.conversations.find((conversation) => conversation[0] === id)[1] = name;
        },
    },
    getters: {
        conversationsIds() {
            return this.conversations.reduce((acc, current) => acc.concat([current[0]]), [])
        },
        getStacks() {
            return (msgId) => {
                // Returns the block of messages of the same type that ends with the last message being msg_id
                for (let i = this.messages.length - 1; i >= 0; i--) {
                    if (this.messages[i].id === msgId)
                        return this.messages[i].stacks;
                }
            }
        }
    }
})
