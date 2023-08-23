import { defineStore } from 'pinia'
function _indexLayerRefs(groupedStack) {
    for (let i = 0; i < groupedStack.length; i++) {
        // first remove the duplicates from the references (same url)
        groupedStack[i].references = groupedStack[i].references.filter((v, i, a) => a.findIndex(t => (t.url === v.url && t.intent === v.intent)) === i)
        // add the reference index to the layer index inside layerToReferences
        let refs = groupedStack[i].references;
        for (let j = 0; j < groupedStack[i].layers.length; j++) {
            const layer = groupedStack[i].layers[j]
            if (layer.payload.references) {
                layer.referenceIndexes = layer.payload.references.map(ref => refs.findIndex(r => r.url === ref.url && r.intent === ref.intent)).filter(i => i !== -1)
            }
        }
    }
}
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
            selectedPlConversationId: undefined,
            // The value of this properties (scrollToBottom, feedbackSent) is irrelevant, what it
            // really matters is the fact that its value changed, which happens every time "New Conversation" button is
            // clicked, then other components will subscribe for any change and react to the fact that has been clicked
            scrollToBottom: 0,
            feedbackSent: 0,
            opened: false,
            deleting: false,
            downloading: false,
            disconnected: true,
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
            console.log(this.conversations)
            this.conversations.find((conversation) => conversation.pk === id).name = name;
        },
        async openConversation(_selectedPlConversationId) {
            const conversationId = this.conversations.find(conv => conv.platform_conversation_id === _selectedPlConversationId).pk
            let response = await fetch(this.chatfaqAPI + `/back/api/broker/conversations/${conversationId}/`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            });
            response = await response.json();
            this.messages = response.mml_chain
            this.selectedPlConversationId = _selectedPlConversationId;
        },
        createNewConversation() {
            this.messages = [];
            this.selectedPlConversationId = Math.floor(Math.random() * 1000000000);
        }
    },
    getters: {
        conversationsIds() {
            return this.conversations.reduce((acc, current) => acc.concat([current.pk]), [])
        },
        getStacks() {
            return (msgId) => {
                // Returns the block of messages of the same type that ends with the last message being msg_id
                for (let i = this.messages.length - 1; i >= 0; i--) {
                    if (this.messages[i].id === msgId)
                        return this.messages[i].stack;
                }
            }
        },
        flatStacks() {
            const res = [];
            const _messages = JSON.parse(JSON.stringify(this.messages));
            let last_lm_msg_payload = {}
            for (let i = 0; i < _messages.length; i++) {
                for (let j = 0; j < _messages[i].stack.length; j++) {
                    const data = _messages[i].stack[j];
                    if (data.type === "lm_generated_text") {
                        if (data.payload.lm_msg_id === last_lm_msg_payload.lm_msg_id) {
                            last_lm_msg_payload.model_response += data.payload.model_response
                            last_lm_msg_payload.references = data.payload.references
                            res[res.length - 1].last = _messages[i].last
                        } else {
                            last_lm_msg_payload = data.payload
                            res.push({..._messages[i], ...data});
                        }
                    } else {
                        res.push({..._messages[i], ...data});
                    }
                }
            }
            return res;
        },
        gropedStacks() {
            // Group stacks by stack_id
            const res = []
            let last_stack_id = undefined
            for (let i = 0; i < this.flatStacks.length; i++) {
                if (this.flatStacks[i].stack_id !== last_stack_id) {
                    res.push({ "layers": [ this.flatStacks[i] ], "references": this.flatStacks[i].payload.references || [], layerToReferences: {} })
                    last_stack_id = this.flatStacks[i].stack_id
                } else {
                    res[res.length - 1].layers.push(this.flatStacks[i])
                    res[res.length - 1].references = res[res.length - 1].references.concat(this.flatStacks[i].payload.references || [])
                }
            }
            _indexLayerRefs(res)
            return res
        },
        waitingForResponse() {
            const gs = this.gropedStacks
            return !gs.length ||
            (gs[gs.length - 1].layers[gs[gs.length - 1].layers.length - 1].sender.type === 'human') ||
            (gs[gs.length - 1].layers[gs[gs.length - 1].layers.length - 1].sender.type === 'bot' &&
            !gs[gs.length - 1].layers[gs[gs.length - 1].layers.length - 1].last)
        },
        lastLayer() {
            const gs = this.gropedStacks;
            if (!gs.length || !gs[gs.length - 1].layers.length)
                return undefined
            return gs[gs.length - 1].layers[gs[gs.length - 1].layers.length - 1]
        }
    }
})
