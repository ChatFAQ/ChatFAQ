import { defineStore } from 'pinia'

export const useGlobalStore = defineStore('globalStore', {
    state: () => {
        return {
            fsmDef: undefined,
            chatfaqWS: undefined,
            chatfaqAPI: undefined,
            userId: undefined,
            title: "",
            subtitle: "",
            darkMode: false,
            menuOpened: false,
            maximized: true,
            historyOpened: true,
            fullScreen: false,
            sourcesFirst: false,
            hideSources: false,
            noHeader: false,
            previewMode: false,
            opened: false,
            fitToParent: false,
            stickInputPrompt: false,
            conversations: [],
            messages: [],
            selectedConversations: [],
            initialSelectedPlConversationId: undefined,
            selectedPlConversationId: undefined,
            // The value of this properties (scrollToBottom, feedbackSent) is irrelevant, what it
            // really matters is the fact that its value changed, which happens every time "New Conversation" button is
            // clicked, then other components will subscribe for any change and react to the fact that has been clicked
            scrollToBottom: 0,
            feedbackSent: 0,
            disconnected: true,
            deleting: false,
            downloading: false,
            isPhone: false,
            initialConversationMetadata: {},
            stateOverwrite: undefined,
            customIFramedMsgs: {},
            speechRecognition: false,
            speechRecognitionAutoSend: false,
            allowAttachments: false,
            authToken: undefined,
            messagesToBeSentSignal: 0,
            messagesToBeSent: [],
            disableDayNightMode: false,
            enableLogout: false,
            enableResend: false,
            resendMsgId: undefined,
            speechSynthesisSupported: 'speechSynthesis' in window,
            speechSynthesisEnabled: false,
            speechSynthesisPitch: 1,
            speechSynthesisRate: 1,
            speechSynthesisVoices: undefined,
            speechRecognitionAlwaysOn: false,
            speechRecognitionLang: 'en-US'
        }
    },
    actions: {
        async gatherConversations() {
            const headers = {}
            if (this.authToken)
                headers.Authorization = `Token ${this.authToken}`;

            let response = await chatfaqFetch(this.chatfaqAPI + `/back/api/broker/conversations/from_sender/?sender=${this.userId}`, { headers });
            this.conversations = await response.json();
        },
        async renameConversationName(id, name) {
            const headers = { 'Content-Type': 'application/json' }
            if (this.authToken)
                headers.Authorization = `Token ${this.authToken}`;

            await chatfaqFetch(this.chatfaqAPI + `/back/api/broker/conversations/${id}/`, {
                method: 'PATCH',
                headers,
                body: JSON.stringify({ name: name })
            });
            this.conversations.find((conversation) => conversation.id === id).name = name;
        },
        async openConversation(_selectedPlConversationId) {
            const headers = { 'Content-Type': 'application/json' }
            if (this.authToken)
                headers.Authorization = `Token ${this.authToken}`;

            const conversationId = this.conversation(_selectedPlConversationId).id
            let response = await chatfaqFetch(this.chatfaqAPI + `/back/api/broker/conversations/${conversationId}/`, {
                method: 'GET',
                headers
            });
            response = await response.json();
            this.messages = response.msgs_chain
            this.selectedPlConversationId = _selectedPlConversationId;
        },
        createNewConversation(selectedPlConversationId) {
            this.messages = [];
            if (!selectedPlConversationId)
                selectedPlConversationId = Math.floor(Math.random() * 1000000000);
            this.selectedPlConversationId = selectedPlConversationId;
        },
        addMessage(message) {
            const index = this.messages.findIndex(m => m.stack_id === message.stack_id)
            if (index !== -1)
                this.messages[index] = message
            else
                this.messages.push(message)
        },
        setPreviewMode() {
            this.previewMode = true
            this.disconnected = false
            this.messages = [{
                "type": "response",
                "status": 200,
                "ctx": {
                    "conversation_id": "168",
                    "user_id": "e35b6551-a323-4d89-a88f-777f8b0f3518"
                },
                "node_type": "action",
                "stack_id": "bb1cbe14-fa72-4698-9e57-c5028a806b69",
                "stack": [{
                    "payload": {"content": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur." },
                    "type": "text",
                    "meta": {
                        "allow_feedback": true
                    }
                }],
                "last": true,
                "sender": {
                    "type": "bot"
                },
                "confidence": 1,
                "send_time": 1718881248945,
                "receiver": {
                    "type": "human",
                    "id": "e35b6551-a323-4d89-a88f-777f8b0f3518"
                },
                "conversation": "168",
                "id": 5379
            }, {
                "sender": {
                    "type": "human",
                    "platform": "WS",
                    "id": "e35b6551-a323-4d89-a88f-777f8b0f3518"
                },
                "stack": [{
                    "type": "text",
                    "payload": {
                       "content": "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
                    }
                }],
                "stack_id": "0",
                "stack_group_id": "0",
                "last": true
            }]
            this.conversations = [
                {
                    "id": 1,
                    "user_id": "e35b6551-a323-4d89-a88f-777f8b0f3518",
                    "rags": [],
                    "created_date": "2024-06-20T13:16:55.622441",
                    "updated_date": "2024-06-20T13:16:55.622549",
                    "platform_conversation_id": "255022336",
                    "name": "Lorem ipsum dolor sit amet."
                },
                {
                    "id": 2,
                    "user_id": "e35b6551-a323-4d89-a88f-777f8b0f3518",
                    "rags": [],
                    "created_date": "2024-06-20T13:02:03.136604",
                    "updated_date": "2024-06-20T13:02:03.136705",
                    "platform_conversation_id": "725628099",
                    "name": "Consectetur adipiscing elit."
                }]
        },
        deleteMsgsAfter(msgId) {
            const msgsToDelete = []
            for (let i = this.messages.length - 1; i >= 0; i--) {
                if (this.messages[i].id === msgId) {
                    this.messages[i].last = true;
                    break;
                }
                msgsToDelete.push(this.messages[i])
            }
            this.messages = this.messages.filter(msg => !msgsToDelete.includes(msg))
        }
    },
    getters: {
        conversationsIds() {
            return this.conversations.reduce((acc, current) => acc.concat([current.id]), [])
        },
        conversation: (state) => (platformConversationId) => {
            return state.conversations.find(conv => conv.platform_conversation_id.toString() === platformConversationId.toString())
        },
        waitingForResponse() {
            const msgs = this.messages || [];
            return !msgs.length ||
            (msgs[msgs.length - 1].sender.type === 'human') ||
            (msgs[msgs.length - 1].sender.type === 'bot' &&
            !msgs[msgs.length - 1].last)
        },
        lastMsg() {
            const msgs = this.messages;
            if (!msgs.length)
                return undefined
            return msgs[msgs.length - 1]
        },
        getMessageById: (state) => (id) => {
            return state.messages.find(m => m.id === id)
        },
        getPrevMsg: (state) => (msg, condition) => {
            const index = state.messages.findIndex(m => m === msg)
            if (index === -1 || index === 0)
                return {}
            // return the message previously that satisfies the condition if
            if (condition) {
                for (let i = index - 1; i >= 0; i--) {
                    if (condition(state.messages[i]))
                        return state.messages[i]
                }
            } else {
                return state.messages[index - 1]
            }
        },
        customIFramedMsg: (state) => (id) => {
            if (state.customIFramedMsgs)
                return state.customIFramedMsgs[id]
        },
        getFeedbackData: (state) => async (msgSourceId) => {
            if (state.previewMode)
                return

            const headers = {}
            if (state.authToken)
                headers.Authorization = `Token ${state.authToken}`;

            let response = await chatfaqFetch(
                state.chatfaqAPI + `/back/api/broker/user-feedback/?message_source=${msgSourceId}`, { headers }
            )
            response = await response.json();
            if (response.results && response.results.length) {
                return response.results[0].feedback_data
            }
        }
    }
})
