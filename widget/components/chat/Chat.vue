<template>
    <div class="chat-wrapper" :class="{ 'dark-mode': store.darkMode }" @click="store.menuOpened = false">
        <div class="conversation-content" ref="conversationContent">
            <ChatMsg
                v-for="(data, index) in flatStacks"
                :is-last-of-type="isLastOfType(data, flatStacks)"
                :is-first-of-type="isFirstOfType(data, flatStacks)"
                :is-first="!flatStacks.indexOf(data)"
                :is-last="flatStacks.indexOf(data) === flatStacks.length -1"
                :data="data"
            ></ChatMsg>
        </div>
        <div class="input-chat-wrapper" :class="{ 'dark-mode': store.darkMode }">
            <input
                :placeholder="$t('writeaquestionhere')"
                v-model="promptValue"
                class="chat-prompt"
                :class="{ 'dark-mode': store.darkMode }"
                ref="chatInput"
                @keyup.enter="sendMessage"
            />
            <i class="chat-send-button" :class="{'dark-mode': store.darkMode}" @click="sendMessage"></i>
        </div>
    </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from "vue";
import { useGlobalStore } from "~/store";

const store = useGlobalStore();

const messages = ref([]);
const promptValue = ref("");
const conversationContent = ref(null)

let ws = undefined
function scrollConversationDown() {
    nextTick(() => {
        conversationContent.value.scroll({top: conversationContent.value.scrollHeight, behavior: "smooth"})
    })
}
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
        if (!messages.value.length) // First message, update list of conversations
            await store.gatherConversations()

        messages.value.push(JSON.parse(e.data));
        console.log(messages)
        scrollConversationDown();
    };
    ws.onopen = async function (e) {
        messages.value = [];
    };
}
createConnection();

watch(() => store.newConversation, createConnection)


const flatStacks = computed(() => {
    const res = [];
    const _messages = messages.value;
    for (let i = 0; i < _messages.length; i++) {
        for (let j = 0; j < _messages[i].stacks.length; j++) {
            for (let k = 0; k < _messages[i].stacks[j].length; k++) {
                const data = _messages[i].stacks[j][k];
                res.push({ ...data, "transmitter": _messages[i]["transmitter"], "id": _messages[i]["id"] });
            }
        }
    }
    return res;
});

function sendMessage() {
    if (!promptValue.value.length)
        return;
    const m = {
        "transmitter": {
            "type": "human",
            "platform": "WS",
        },
        "stacks": [[{
            "type": "text",
            "payload": promptValue.value,
        }]],
    };
    if (store.userId !== undefined)
        m["transmitter"]["id"] = store.userId

    messages.value.push(m);
    ws.send(JSON.stringify(m));
    promptValue.value = "";
    scrollConversationDown();
}

function isLastOfType(msg, flatStack) {
    if (flatStack.indexOf(msg) === flatStack.length - 1)
        return true
    if (flatStack[flatStack.indexOf(msg) + 1].transmitter.type !== msg.transmitter.type)
        return true
    return false
}

function isFirstOfType(msg, flatStack) {
    if (!flatStack.indexOf(msg))
        return true
    if (flatStack[flatStack.indexOf(msg) - 1].transmitter.type !== msg.transmitter.type)
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
        background-color: $chatfaq-color-neutral-black;
    }
}

.input-chat-wrapper {
    display: flex;
    width: 100%;
    border-top: 1px solid $chatfaq-color-neutral-black !important;

    &.dark-mode {
        border-top: 1px solid $chatfaq-color-secondary-500 !important;
    }
}

.conversation-content {
    height: 100%;
    width: 100%;
    overflow: scroll;

    &::-webkit-scrollbar {
        display: none;
    }
}

.chat-prompt, .chat-prompt:focus, .chat-prompt:hover {
    width: 100%;
    border: 0;
    outline: 0;
    margin-left: 24px;
    background-color: $chatfaq-color-primary-200;
}


.chat-prompt {
    font: $chatfaq-font-caption-md;
    font-style: normal;

    &::placeholder {
        font-style: italic;
        color: rgb(2, 12, 28);
    }

    &.dark-mode {
        background-color: $chatfaq-color-neutral-black;
        color: $chatfaq-color-primary-200;

        &::placeholder {
            color: $chatfaq-color-neutral-white;
        }
    }
}

.chat-send-button, .chat-send-button:focus, .chat-send-button:hover {
    content: $chatfaq-send-icon;
    margin: 22px 26px 22px 20px;
    cursor: pointer;

    &.dark-mode {
        content: $chatfaq-send-dark-icon;
    }
}

</style>
