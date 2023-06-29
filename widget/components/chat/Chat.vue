<template>
    <div class="chat-wrapper" :class="{ 'dark-mode': store.darkMode }" @click="store.menuOpened = false">
        <div class="conversation-content" ref="conversationContent" :class="{'dark-mode': store.darkMode}">
            <div class="stacks" v-for="(layers, index) in gropedStacks">
                <ChatMsg
                    :layers="layers"
                    :is-last-of-type="true"
                    :is-first-of-type="true"
                    :is-first="index === 0"
                    :is-last="index === gropedStacks.length - 1"
                ></ChatMsg>
            </div>
            <LoaderMsg v-if="waitingForResponse" ></LoaderMsg>
        </div>
        <div class="feedback-message" :class="{ 'fade-out': feedbackSentDisabled, 'dark-mode': store.darkMode }">{{ $t("feedbacksent") }}</div>
        <div class="input-chat-wrapper" :class="{ 'dark-mode': store.darkMode }">
            <div
                :placeholder="$t('writeaquestionhere')"
                class="chat-prompt"
                :class="{ 'dark-mode': store.darkMode, 'maximized': store.maximized }"
                ref="chatInput"
                @keyup.enter="sendMessage"
                @keypress.enter.prevent
                contenteditable
                oninput="if(this.innerHTML.trim()==='<br>')this.innerHTML=''"
                @input="($event)=>thereIsContent = $event.target.innerHTML.length !== 0"
            />
            <i class="chat-send-button" :class="{'dark-mode': store.darkMode, 'active': thereIsContent}" @click="sendMessage"></i>
        </div>
    </div>
</template>

<script setup>
import {ref, computed, watch, nextTick} from "vue";
import {useGlobalStore} from "~/store";
import LoaderMsg from "~/components/chat/LoaderMsg.vue";

const store = useGlobalStore();

const chatInput = ref(null);
const conversationContent = ref(null)
const feedbackSentDisabled = ref(true)
const thereIsContent = ref(false)

let ws = undefined

watch(() => store.scrollToBottom, scrollConversationDown)
watch(() => store.selectedPlConversationId, createConnection)
watch(() => store.feedbackSent, animateFeedbackSent)

function scrollConversationDown() {
    nextTick(() => {
        conversationContent.value.scroll({top: conversationContent.value.scrollHeight, behavior: "smooth"})
    })
}

function animateFeedbackSent() {
    feedbackSentDisabled.value = false
    setTimeout(() => {
        feedbackSentDisabled.value = true
    }, 1500)
}


function createConnection() {
    if (ws)
        ws.close()

    ws = new WebSocket(
        store.chatfaqWS
        + "/back/ws/broker/"
        + store.selectedPlConversationId
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
}

store.createNewConversation()

const flatStacks = computed(() => {
    const res = [];
    const _messages = JSON.parse(JSON.stringify(store.messages));
    let last_lm_msg_payload = {}
    for (let i = 0; i < _messages.length; i++) {
        for (let j = 0; j < _messages[i].stack.length; j++) {
            const data = _messages[i].stack[j];
            if (data.type === "lm_generated_text") {
                if (data.payload.lm_msg_id === last_lm_msg_payload.lm_msg_id) {
                    last_lm_msg_payload.model_response += data.payload.model_response
                    last_lm_msg_payload.references = data.payload.references
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
});

const gropedStacks = computed(() => {
    // Group stacks by stack_id
    const res = []
    let last_stack_id = undefined
    for (let i = 0; i < flatStacks.value.length; i++) {
        if (flatStacks.value[i].stack_id !== last_stack_id) {
            res.push([flatStacks.value[i]])
            last_stack_id = flatStacks.value[i].stack_id
        } else {
            res[res.length - 1].push(flatStacks.value[i])
        }
    }
    return res
});
const waitingForResponse = computed(() => {
    const gs = gropedStacks.value
    return !gs.length ||
    (gs[gs.length - 1][gs[gs.length - 1].length - 1].sender.type === 'human') ||
    (gs[gs.length - 1][gs[gs.length - 1].length - 1].sender.type === 'bot' &&
    !gs[gs.length - 1][gs[gs.length - 1].length - 1].last)
})


function sendMessage(ev) {
    const promptValue = chatInput.value.innerText.trim()
    if (!promptValue.length)
        return;
    const m = {
        "sender": {
            "type": "human",
            "platform": "WS",
        },
        "stack": [{
            "type": "text",
            "payload": promptValue,
        }],
        "stack_id": "0",
        "last": true,
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
@import "assets/styles/mixins";

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

.feedback-message {
    margin-bottom: -16px;
    text-align: center;
    color: $chatfaq-color-greyscale-800;
    .fade-out {
        animation: shake 0.82s cubic-bezier(0.36, 0.07, 0.19, 0.97) both;
        transform: translate3d(0, 0, 0);
    }
    &.dark-mode {
        color: $chatfaq-color-primary-200;
    }
}
.fade-out {
    visibility: hidden;
    opacity: 0;
    transition: visibility 0s 2s, opacity 2s linear;
}

.conversation-content {
    height: 100%;
    width: 100%;
    overflow-x: hidden;

    @include scroll-style();
    &.dark-mode {
        @include scroll-style(white);
    }
}

.chat-prompt, .chat-prompt:focus, .chat-prompt:hover {
    width: 100%;
    border: 0;
    outline: 0;
    margin-left: 16px;
    background-color: $chatfaq-color-primary-300;
    @include scroll-style();
    &.dark-mode {
        @include scroll-style(white);
    }
}

[contenteditable][placeholder]:empty:before {
    content: attr(placeholder);
    position: absolute;
    color: rgba(2, 12, 28, 0.6);
    background-color: transparent;
    font-style: italic;
    cursor: text;
}
.dark-mode[contenteditable][placeholder]:empty:before {
    color: $chatfaq-color-primary-200;
}
.chat-prompt {
    font: $chatfaq-font-caption-md;
    font-style: normal;
    min-height: 1em;
    overflow-x: hidden;
    overflow-y: auto;
    margin-top: auto;
    margin-bottom: auto;
    max-height: 80px;

    &.maximized {
        max-height: 190px;
    }

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
    margin: 11px 16px;
    cursor: pointer;
    height: 16px;
    align-self: end;
    opacity: 0.6;

    &.dark-mode {
        content: $chatfaq-send-dark-icon;
    }
    &.active {
        opacity: 1;
    }
}

</style>
