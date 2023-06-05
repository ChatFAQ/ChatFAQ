<template>
    <div class="chat-wrapper" :class="{ 'dark-mode': store.darkMode }" @click="store.menuOpened = false">
        <div class="conversation-content" ref="conversationContent">
            <ChatMsg
                v-for="data in flatStacks"
                :is-last-of-type="isLastOfType(data, flatStacks)"
                :is-first-of-type="isFirstOfType(data, flatStacks)"
                :is-first="!flatStacks.indexOf(data)"
                :is-last="flatStacks.indexOf(data) === flatStacks.length -1"
                :data="data"
            ></ChatMsg>
        </div>
        <div class="input-chat-wrapper" :class="{ 'dark-mode': store.darkMode }">
            <div
                :placeholder="$t('writeaquestionhere')"
                class="chat-prompt"
                :class="{ 'dark-mode': store.darkMode }"
                ref="chatInput"
                @keyup.enter="sendMessage"
                @keypress.enter.prevent
                contenteditable
            />
            <i class="chat-send-button" :class="{'dark-mode': store.darkMode}" @click="sendMessage"></i>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from "vue";
import { useGlobalStore } from "~/store";

const store = useGlobalStore();

const chatInput = ref(null);
const conversationContent = ref(null)

let ws = undefined
function scrollConversationDown() {
    nextTick(() => {
        conversationContent.value.scroll({top: conversationContent.value.scrollHeight, behavior: "smooth"})
    })
}
watch(() => store.scrollToBottom, scrollConversationDown)

function createConnection() {
    if (ws)
        ws.close()

    const conversationID = Math.floor(Math.random() * 1000000000);
    ws = new WebSocket(
        store.chatfaqWS
        + "/back/ws/broker/"
        + conversationID
        + "/"
        + store.fsmDef
        + "/"
        + (store.userId ? `${store.userId}/` : "")
    );
    ws.onmessage = async function (e) {
        if (!store.messages.length) // First message, update list of conversations
            await store.gatherConversations()

        store.messages.push(JSON.parse(e.data));
        store.scrollToBottom += 1;
    };
    ws.onopen = async function (e) {
        store.messages = [];
    };
}

createConnection();

watch(() => store.newConversation, createConnection)

const flatStacks = computed(() => {
    const res = [];
    const _messages = store.messages;
    for (let i = 0; i < _messages.length; i++) {
        for (let j = 0; j < _messages[i].stacks.length; j++) {
            for (let k = 0; k < _messages[i].stacks[j].length; k++) {
                const data = _messages[i].stacks[j][k];
                res.push({ ...data, "sender": _messages[i]["sender"], "id": _messages[i]["id"] });
            }
        }
    }
    return res;
});

function sendMessage(ev) {
    const promptValue = chatInput.value.innerText.trim()
    if (!promptValue.length)
        return;
    const m = {
        "sender": {
            "type": "human",
            "platform": "WS",
        },
        "stacks": [[{
            "type": "text",
            "payload": promptValue,
        }]],
    };
    if (store.userId !== undefined)
        m["sender"]["id"] = store.userId

    store.messages.push(m);
    ws.send(JSON.stringify(m));
    chatInput.value.innerText = "";
    store.scrollToBottom += 1;
}

function isLastOfType(msg, flatStack) {
    if (flatStack.indexOf(msg) === flatStack.length - 1)
        return true
    if (flatStack[flatStack.indexOf(msg) + 1].sender.type !== msg.sender.type)
        return true
    return false
}

function isFirstOfType(msg, flatStack) {
    if (!flatStack.indexOf(msg))
        return true
    if (flatStack[flatStack.indexOf(msg) - 1].sender.type !== msg.sender.type)
        return true
    return false
}

</script>
<style scoped lang="scss">
@import "assets/styles/variables";

.chat-wrapper {
    font: $chatfaq-font-body-s;
    font-style: normal;
    position: absolute;
    height: 100%;
    width: 100%;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background-color: $chatfaq-color-primary-200;

    &.dark-mode {
        background-color: $chatfaq-color-neutral-purple;
    }
}

.input-chat-wrapper {
    margin: 24px;
    display: flex;
    border-radius: 4px;
    border: 1px solid $chatfaq-color-neutral-purple !important;
    background-color: $chatfaq-color-primary-300;
    box-shadow: 0px 4px 4px rgba(70, 48, 117, 0.1);

    &.dark-mode {
        background-color: $chatfaq-color-primary-800;
        border: 1px solid $chatfaq-color-primary-900 !important;
    }
}

.conversation-content {
    height: 100%;
    width: 100%;
    overflow: scroll;

    /* Scroll */
    &::-webkit-scrollbar {
        width: 6px;
    }

    &::-webkit-scrollbar-track {
        box-shadow: inset 0 0 6px 6px transparent;
        border: solid 2px transparent;
    }

    &::-webkit-scrollbar-thumb {
        box-shadow: inset 0 0 6px 6px $chatfaq-color-primary-500;
        border: solid 2px transparent;
    }
}

.chat-prompt, .chat-prompt:focus, .chat-prompt:hover {
    width: 100%;
    border: 0;
    outline: 0;
    margin-left: 16px;
    background-color: $chatfaq-color-primary-300;
}


.chat-prompt {
    font: $chatfaq-font-caption-md;
    font-style: normal;
    min-height: 1em;
    max-height: 80px;
    overflow-x: hidden;
    overflow-y: auto;
    margin-top: auto;
    margin-bottom: auto;
    /* Scroll */
    /*
    &::-webkit-scrollbar {
        width: 6px;
    }
    &::-webkit-scrollbar-track {
        box-shadow: inset 0 0 6px 6px transparent;
        border: solid 2px transparent;
    }
    &::-webkit-scrollbar-thumb {
        box-shadow: inset 0 0 6px 6px $chatfaq-color-primary-500;
        border: solid 2px transparent;
    }
    */
    &::placeholder {
        font-style: italic;
        color: rgb(2, 12, 28);
    }

    &.dark-mode {
        background-color: $chatfaq-color-primary-800;
        color: $chatfaq-color-primary-200;

        &::placeholder {
            color: $chatfaq-color-neutral-white;
        }
    }
}

.chat-send-button, .chat-send-button:focus, .chat-send-button:hover {
    content: $chatfaq-send-icon;
    margin-top: 11px;
    margin-bottom: 11px;
    margin-right: 16px;
    cursor: pointer;

    &.dark-mode {
        content: $chatfaq-send-dark-icon;
    }
}

</style>
