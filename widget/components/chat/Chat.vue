<template>
    <div class="chat-wrapper" :class="{ 'dark-mode': store.darkMode, 'fit-to-parent': store.fitToParent, 'stick-input-prompt': store.stickInputPrompt, 'split-screen': store.splitScreenIframe}" @click="store.menuOpened = false">
        <div class="right-content">
            <div class="conversation-content" ref="conversationContent" :class="{'dark-mode': store.darkMode, 'fit-to-parent-conversation-content': store.fitToParent}">
                <div class="stacks" :class="{'merge-to-prev': getFirstLayerMergeToPrev(message)}" v-for="(message, index) in store.messages">
                    <ChatMsgManager
                        v-if="isRenderableStackType(message)"
                        :message="message"
                        :key="message.stack_id"
                        :is-last-of-type="isLastOfType(index)"
                        :is-first="index === 0"
                        :is-last="index === store.messages.length - 1"
                    ></ChatMsgManager>
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
            <ChatPrompt @send="(msg) => sendMessage(msg)"/>
        </div>
        <div v-if="store.splitScreenIframe" class="split-screen-iframe-container">
            <iframe
                class="split-screen-iframe"
                :src="store.splitScreenIframe"
                allowfullscreen
            ></iframe>
        </div>
    </div>
</template>

<script setup>
import {ref, watch, nextTick, onMounted} from "vue";
import {useGlobalStore} from "~/store";
import LoaderMsg from "~/components/chat/LoaderMsg.vue";
import ChatMsgManager from "~/components/chat/msgs/ChatMsgManager.vue";
import ChatPrompt from "~/components/chat/ChatPrompt.vue";

const store = useGlobalStore();

const chatInput = ref(null);
const conversationContent = ref(null)
const feedbackSentDisabled = ref(true)
const notRenderableStackTypes = ["gtm_tag", "close_conversation", undefined]

let ws = undefined

watch(() => store.scrollToBottom, scrollConversationDown)
watch(() => store.selectedPlConversationId, createConnection)
watch(() => store.feedbackSent, animateFeedbackSent)
watch(() => store.resendMsgId, resendMsg)
watch(() => store.messagesToBeSentSignal, sendMessagesToBeSent)
watch(() => store.selectedPlConversationId, () => {
    store.conversationClosed = false
})

onMounted(async () => {
    await initializeConversation()
})

function isLastOfType(index) {
    return index === store.messages.length - 1 || store.messages[index + 1].sender.type !== store.messages[index].sender.type
}
function getFirstLayerMergeToPrev(message) {
    return message?.stack[0]?.payload.merge_to_prev;
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
function isRenderableStackType(message) {
    return !notRenderableStackTypes.includes(message.stack[0]?.type)
}

function createConnection() {
    if(store.previewMode)
        return

    if (ws)
        ws.close()

    let queryParams = ""
    if (store.initialConversationMetadata)
        queryParams = `?metadata=${JSON.stringify(store.initialConversationMetadata)}`

    if (store.authToken && store.authToken.length) {
        if (queryParams.length) queryParams += "&"
        else queryParams = "?"
        queryParams += `token=${encodeURIComponent(store.authToken)}`
    }


    if (store.stateOverride) {
        if (queryParams.length) {
            queryParams += "&"
        } else {
            queryParams = "?"
        }
        queryParams += `state_override=${encodeURIComponent(store.stateOverride)}`
    }

    ws = new WebSocket(
        store.chatfaqWS
        + "/back/ws/broker/"
        + store.selectedPlConversationId
        + "/"
        + store.fsmDef
        + "/"
        + (store.userId ? `${store.userId}/${queryParams}` : "")
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
        if (msg.stack[0]?.type === 'close_conversation')
            store.conversationClosed = true

        sendToGTM(msg)
        store.addMessage(msg);
        if(store.messages.length === 1)
            await store.gatherConversations()
    };
    ws.onopen = async function () {
        store.disconnected = false;
        // await store.gatherConversations()
    };
    const plConversationId = store.selectedPlConversationId
    ws.onclose = function (e) {
        if (e.code === 4000 || e.code === 3000) {  // SDK not existent or RPC worker not connected || Authentication error
            let _msg = e.reason
            store.addMessage({
                "sender": {
                    "type": "bot",
                    "platform": "WS",
                },
                "stack": [{
                    "type": "message",
                    "payload": {
                        "content": _msg
                    },
                }],
                "stack_id": Math.random().toString(36).substring(7),
                "stack_group_id": Math.random().toString(36).substring(7),
                "last": true,
            });
            return;
        }
        if (plConversationId !== store.selectedPlConversationId)
            return;
        store.disconnected = true;
        setTimeout(function () {
            createConnection();
        }, 1000);
    };
}


async function initializeConversation() {
    if(store.previewMode)
        return

    if (store.initialSelectedPlConversationId) {
        await store.gatherConversations()
        if (store.conversation(store.initialSelectedPlConversationId)) {
            return await store.openConversation(store.initialSelectedPlConversationId);
        }
    }
    store.conversationClosed = false
    store.createNewConversation(store.initialSelectedPlConversationId);
}

function sendMessage(message) {
    if (!store.canSendMsg)
        return;

    if (!message)
        return

    store.messages.push(message);
    ws.send(JSON.stringify(message));
    store.scrollToBottom += 1;

    chatInput.value?.blur(); // Remove focus from the input
}

function sendMessagesToBeSent() {
    if(!store.canSendMsg) {
        setTimeout(() => sendMessagesToBeSent(), 1000)
        return
    }

    while (store.messagesToBeSent.length) {
        sendMessage(store.messagesToBeSent.pop());
    }
}

function resendMsg(msgId) {
    if (msgId === undefined)
        return;
    if (store.disconnected)
        return;
    store.deleteMsgsAfter(msgId)
    ws.send(JSON.stringify({reset: msgId}));
}

function sendToGTM(msg) {
    if (msg?.stack?.length && msg.stack[0].type === "gtm_tag") {
        if (window?.dataLayer)
            window.dataLayer.push(msg.stack[0].payload);
        else
            console.warn("GTM tag received but no dataLayer found")
    }
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
    background-color: $chatfaq-color-chat-background-light;
    &.split-screen {
        flex-direction: row;
        overflow: hidden !important;
    }
    .right-content {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
        width: 100%;

    }
    .split-screen-iframe-container {
        height: 100%;
        width: 100%;
        box-shadow: 0px 2px 18px 0px #0000001A;
    }
    .split-screen-iframe {
        height: 100%;
        width: 100%;
        border: 0;
    }
    &.dark-mode {
        background-color: $chatfaq-color-chat-background-dark;
    }
    &.fit-to-parent {
        border: unset !important;
        border-radius: inherit !important;
        overflow: hidden;
    }

    &.stick-input-prompt {
        overflow: initial !important;
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
    overflow-x: hidden;

    @include scroll-style();

    &.dark-mode {
        @include scroll-style($chatfaq-color-scrollBar-dark);
    }
    &.fit-to-parent-conversation-content {
        min-height: inherit;
    }
}

.merge-to-prev {
    display: none;
}
</style>
