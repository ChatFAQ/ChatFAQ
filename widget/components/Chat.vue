<template>
    <div class="chat-wrapper">
        <div class="conversation-content">
            <div v-for="data in flatStacks" class="message" :class="data.transmitter.type">
                {{ data.payload }}
            </div>
        </div>
        <div class="input-chat-wrapper">
            <InputText v-model="promptValue" class="chat-prompt" ref="chatInput" @keyup.enter="sendMessage" />
            <Button class="chat-send-button" @click="sendMessage"><i class="pi pi-send"></i></Button>
        </div>
    </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useGlobalStore } from '~/store'
const store = useGlobalStore();

const messages = ref([]);
const promptValue = ref("");
const conversationID = Math.floor(Math.random() * 1000000000);

const ws = new WebSocket(
    store.chatfaqWS
    + "/back/ws/broker/"
    + conversationID
    + "/"
    + store.selectedFSMDef.id
    + "/",
);
ws.onmessage = function(e) {
    messages.value.push(JSON.parse(e.data));
};
ws.onclose = function(e) {
    console.error("Chat socket closed unexpectedly");
};

const flatStacks = computed(() => {
    const res = [];
    const _messages = messages.value;
    for (let i = 0; i < _messages.length; i++) {
        for (let j = 0; j < _messages[i].stacks.length; j++) {
            for (let k = 0; k < _messages[i].stacks[j].length; k++) {
                const data = _messages[i].stacks[j][k];
                res.push({ ...data, "transmitter": _messages[i]["transmitter"] });
            }
        }
    }
    return res;
});

function sendMessage() {
    if (!promptValue.value.length)
        return;
    const m = {
        "transmitter": { "type": "user" },
        "stacks": [[{
            "type": "text",
            "payload": promptValue.value,
        }]],
    };
    messages.value.push(m);
    ws.send(JSON.stringify(m));
    promptValue.value = "";
}
</script>
<style scoped lang="scss">
@import "../assets/styles/variables";

.chat-wrapper {
    position: absolute;
    height: 100%;
    width: 100%;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.input-chat-wrapper {
    display: flex;
    width: 100%;
}

.conversation-content {
    height: 100%;
    width: 100%;
    overflow: scroll;
}

.chat-prompt, .chat-prompt:focus, .chat-prompt:hover {
    width: 100%;
    box-shadow: none !important;
    border: none !important;
    border-top: 1px solid !important;
    border-color: $main-color !important;
}

.chat-send-button, .chat-send-button:focus, .chat-send-button:hover {
    box-shadow: none !important;
    border-color: $main-color !important;
    background-color: $main-color !important;
}

.message {
    border: solid 1px;
    width: fit-content;
    margin: 5px;
    padding: 5px;
    border-radius: 5px;

    &.bot {
        border-color: $main-color;
    }

    &.user {
        border-color: #8E93FF;
        margin-left: auto;
    }
}
</style>
