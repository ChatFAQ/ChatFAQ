<template>
    <div class="chat-wrapper" :class="{ 'dark-mode': store.darkMode }" @click="store.menuOpened = false">
        <div class="conversation-content" ref="conversationContent" :class="{'dark-mode': store.darkMode}">
            <div class="stacks" v-for="(message, index) in store.messages">
                <ChatMsg
                    :message="message"
                    :key="message.stack_id"
                    :is-last-of-type="isLastOfType(index)"
                    :is-first="index === 0"
                    :is-last="index === store.messages.length - 1"
                ></ChatMsg>
            </div>
            <LoaderMsg v-if="store.waitingForResponse"></LoaderMsg>
        </div>
        <div class="alert-message" :class="{ 'fade-out': feedbackSentDisabled, 'dark-mode': store.darkMode }">
            {{ $t("feedbacksent") }}
        </div>
        <div class="alert-message"
             :class="{ 'fade-out': !store.disconnected, 'dark-mode': store.darkMode, 'pulsating': store.disconnected }">
            {{ $t("connectingtoserver") }}
        </div>
        <div class="input-chat-wrapper" :class="{ 'dark-mode': store.darkMode }">
            <div
                :placeholder="$t('writeaquestionhere')"
                class="chat-prompt"
                :class="{ 'dark-mode': store.darkMode, 'maximized': store.maximized }"
                ref="chatInput"
                @keydown="(ev) => manageEnterInput(ev, sendMessage)"
                contenteditable
                oninput="if(this.innerHTML.trim()==='<br>')this.innerHTML=''"
                @input="($event)=>thereIsContent = $event.target.innerHTML.length !== 0"
                @paste="managePaste"
            />
            <i class="chat-send-button"
               :class="{'dark-mode': store.darkMode, 'active': thereIsContent && !store.waitingForResponse}"
               @click="sendMessage"></i>
        </div>
    </div>
</template>

<script setup>
import {ref, watch, nextTick} from "vue";
import {useGlobalStore} from "~/store";
import LoaderMsg from "~/components/chat/LoaderMsg.vue";
import ChatMsg from "~/components/chat/msgs/ChatMsg.vue";

const store = useGlobalStore();

const chatInput = ref(null);
const conversationContent = ref(null)
const feedbackSentDisabled = ref(true)
const thereIsContent = ref(false)

let ws = undefined
let heartbeatTimeout = undefined

watch(() => store.scrollToBottom, scrollConversationDown)
watch(() => store.selectedPlConversationId, createConnection)
watch(() => store.feedbackSent, animateFeedbackSent)

function isLastOfType(index) {
    return index === store.messages.length - 1 || store.messages[index + 1].sender.type !== store.messages[index].sender.type
}

function managePaste(ev) {
    ev.preventDefault()
    const text = ev.clipboardData.getData('text/plain').replace(/\n\r?/g, "<br>");
    ev.target.innerHTML = text
}

function scrollConversationDown() {
    nextTick(() => {
        conversationContent.value.scroll({top: conversationContent.value.scrollHeight, behavior: "smooth"})
    })
}

function isFullyScrolled() {
    return conversationContent.value.scrollHeight - conversationContent.value.scrollTop === conversationContent.value.clientHeight
}

function animateFeedbackSent() {
    feedbackSentDisabled.value = false
    setTimeout(() => {
        feedbackSentDisabled.value = true
    }, 1500)
}

function createHeartbeat(ws) {
    ws.send(JSON.stringify({
        "heartbeat": true
    }));
    heartbeatTimeout = setTimeout(() => {
        createHeartbeat(ws)
    }, 5000)

}

function deleteHeartbeat() {
    clearTimeout(heartbeatTimeout)
}


function createConnection() {
    if(store.previewMode)
        return

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
        const msg = JSON.parse(e.data);
        if (msg.status === 400) {
            console.error(`Error in message from WS: ${msg.payload}`)
            return
        }

        if (store.lastMsg && store.lastMsg.sender.type === 'human')  // Scroll down if brand a new message from bot just came
            store.scrollToBottom += 1;
        if (isFullyScrolled())  // Scroll down if user is at the bottom
            store.scrollToBottom += 1;

        store.addMessage(msg);
        if (store.messages.length === 1) // First message, update list of conversations
            await store.gatherConversations()
    };
    ws.onopen = function (e) {
        store.disconnected = false;
        createHeartbeat(ws)
    };
    const plConversationId = store.selectedPlConversationId
    ws.onclose = function (e) {
        deleteHeartbeat();
        if (plConversationId !== store.selectedPlConversationId)
            return;
        store.disconnected = true;
        setTimeout(function () {
            createConnection();
        }, 1000);
    };
}


if(!store.previewMode)
    store.createNewConversation()

function manageEnterInput(ev, cb) {
    if (ev.key === 'Enter' && !ev.shiftKey) {
        ev.preventDefault()
        cb();
    }
};

function sendMessage() {
    const promptValue = chatInput.value.innerText.trim()
    if (!promptValue.length || store.waitingForResponse || store.disconnected)
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


</script>
<style scoped lang="scss">

.chat-wrapper {
    font: $chatfaq-font-body-s;
    font-style: normal;
    position: absolute;
    height: 100%;
    width: 100%;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    background-color: $chatfaq-color-chat-background-light;

    &.dark-mode {
        background-color: $chatfaq-color-chat-background-dark;
    }
}

.input-chat-wrapper {
    margin: 24px;
    display: flex;
    border-radius: 4px;
    border: 1px solid $chatfaq-color-chatInput-border-light !important;
    background-color: $chatfaq-color-chatInput-background-light;
    box-shadow: 0px 4px 4px rgba(70, 48, 117, 0.1);

    &.dark-mode {
        background-color: $chatfaq-color-chatInput-background-dark;
        border: 1px solid $chatfaq-color-chatInput-border-dark !important;
    }
}

.alert-message {
    margin-bottom: -16px;
    text-align: center;
    color: $chatfaq-color-alertMessage-text-light;

    &.dark-mode {
        color: $chatfaq-color-alertMessage-text-dark;
    }
}


.pulsating {
    animation-duration: 2s;
    animation-name: pulsating;
    animation-iteration-count: infinite;
    animation-direction: alternate;
}

@keyframes pulsating {
    0% {
        opacity: 100%;
    }
    50% {
        opacity: 30%;
    }
    100% {
        opacity: 100%;
    }
}

.fade-out {
    animation: shake 0.82s cubic-bezier(0.36, 0.07, 0.19, 0.97) both;
    transform: translate3d(0, 0, 0);
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
    word-wrap: break-word;
    border: 0;
    outline: 0;
    margin-left: 16px;
    background-color: transparent;
    color: $chatfaq-color-chatInput-text-light;
    @include scroll-style();

    &.dark-mode {
        @include scroll-style(white);
    }
}

[contenteditable][placeholder]:empty:before {
    content: attr(placeholder);
    position: absolute;
    color: $chatfaq-color-chatPlaceholder-text-light;
    background-color: transparent;
    font-style: italic;
    cursor: text;
}

.dark-mode[contenteditable][placeholder]:empty:before {
    color: $chatfaq-color-chatPlaceholder-text-dark;
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
        color: $chatfaq-color-chatInput-text-light;
    }

    &.dark-mode {
        color: $chatfaq-color-chatPlaceholder-text-dark;

        &::placeholder {
            color: $chatfaq-color-chatInput-text-dark;
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
