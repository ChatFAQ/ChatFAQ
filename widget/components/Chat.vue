<template>
    <div class="chat-wrapper"  :class="{ 'dark-mode': store.darkMode }" @click="store.menuOpened = false">
        <div class="conversation-content">
            <div
                v-for="data in flatStacks"
                class="message"
                :class=" {
                    [data.transmitter.type]: true,
                    'is-last-of-type': isLastOfType(data, flatStacks),
                    'is-first-of-type': isFirstOfType(data, flatStacks),
                    'is-first': !flatStacks.indexOf(data),
                    'is-last': flatStacks.indexOf(data) === flatStacks.length -1,
                    'dark-mode': store.darkMode
                }
            ">
                {{ data.payload }}
            </div>
        </div>
        <div class="input-chat-wrapper" :class="{ 'dark-mode': store.darkMode }">
            <input
                placeholder="Write a question here..."
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
import {ref, computed} from "vue";
import {useGlobalStore} from "~/store";

const store = useGlobalStore();

const messages = ref([]);
const promptValue = ref("");
const conversationID = Math.floor(Math.random() * 1000000000);

const ws = new WebSocket(
    store.chatfaqWS
    + "/back/ws/broker/"
    + conversationID
    + "/"
    + store.fsmDef
    + "/",
);
ws.onmessage = function (e) {
    messages.value.push(JSON.parse(e.data));
};
ws.onclose = function (e) {
    console.error("Chat socket closed unexpectedly");
};

const flatStacks = computed(() => {
    const res = [];
    const _messages = messages.value;
    for (let i = 0; i < _messages.length; i++) {
        for (let j = 0; j < _messages[i].stacks.length; j++) {
            for (let k = 0; k < _messages[i].stacks[j].length; k++) {
                const data = _messages[i].stacks[j][k];
                res.push({...data, "transmitter": _messages[i]["transmitter"]});
            }
        }
    }
    return res;
});

function sendMessage() {
    if (!promptValue.value.length)
        return;
    const m = {
        "transmitter": {"type": "user"},
        "stacks": [[{
            "type": "text",
            "payload": promptValue.value,
        }]],
    };
    messages.value.push(m);
    ws.send(JSON.stringify(m));
    promptValue.value = "";
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
@import "../assets/styles/variables";

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
    &.dark-mode  {
        background-color: $chatfaq-color-neutral-black;
    }
}

.input-chat-wrapper {
    display: flex;
    width: 100%;
    border-top: 1px solid $chatfaq-color-neutral-black !important;

    &.dark-mode  {
        border-top: 1px solid $chatfaq-color-secondary-500 !important;
    }
}

.conversation-content {
    height: 100%;
    width: 100%;
    overflow: scroll;
    display: flex;
    flex-direction: column;
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

    &.dark-mode  {
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


.message {
    border: solid 1px;
    width: fit-content;
    margin: 8px 5px 0px;
    padding: 5px;
    border-radius: 20px;
    padding: 9px 15px 9px 15px;
    max-width: 90%;
    word-wrap: break-word;

    &.is-first-of-type {
        margin-top: 16px;
    }
    &.is-first {
        margin-top: 20px;
    }
    &.is-last {
        margin-bottom: 20px;
    }

    &.bot {
        border-color: $chatfaq-color-primary-500;
        color: $chatfaq-color-neutral-black;
        margin-left: 24px;
        &.is-last-of-type {
            border-radius: 20px  20px  20px  0px;
        }
        &.dark-mode  {
            background-color: $chatfaq-color-neutral-black;
            border-color: $chatfaq-color-secondary-500;
            color: $chatfaq-color-neutral-white;
        }
    }

    &.user {
        border: none;
        background-color: $chatfaq-color-primary-500;
        color: $chatfaq-color-neutral-white;
        align-self: end;
        margin-right: 24px;
        &.is-last-of-type {
            border-radius: 20px  20px  0px  20px;
        }
    }
}
</style>
