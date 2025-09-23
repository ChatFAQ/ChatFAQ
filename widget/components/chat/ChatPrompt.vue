<template>
    <div class="chat-prompt-wrapper" :class="{ 'dark-mode': store.darkMode, 'fit-to-parent-prompt': store.fitToParent }">
        <div class="chat-prompt-outer">
            <Attach v-if="store.allowAttachments" class="attach-buttom"/>
            <div
                :placeholder="$t('writeaquestionhere')"
                class="chat-prompt"
                :contenteditable="store.promptEditable"
                :class="{
                    'dark-mode': store.darkMode,
                    'maximized': store.maximized,
                    'disabled': !store.promptEditable
                }"
                ref="chatInput"
                @keydown="(ev) => manageHotKeys(ev)"
                @input="($event)=>{store.promptWithText = $event.target.innerHTML.trim().length !== 0 && $event.target.innerHTML.trim() !== '<br>'; }"
            />
        </div>
        <PromptControls @send="emit('send', createSendMessage())" @text="(text) => {chatInput.innerText = text; store.promptWithText = text.trim().length !== 0}"/>
    </div>
</template>
<script setup>
import {ref} from "vue";

import PromptControls from "~/components/chat/PromptControls.vue";
import Attach from "~/components/icons/Attach.vue";
import {useGlobalStore} from "~/store";

const store = useGlobalStore();

let historyIndexHumanMsg = -1

const chatInput = ref(null);

const emit = defineEmits(['send'])


function manageHotKeys(ev) {
    const _s = window.getSelection()
    const _r = window.getSelection().getRangeAt(0)
    const atTheBeginning = _r.endOffset === 0 && !_r.previousSibling;
    const atTheEnd = _r.endOffset === _s.focusNode.length && !_r.endContainer.nextSibling;

    if (ev.key === 'Enter' && !ev.shiftKey) {
        ev.preventDefault()
        emit('send', createSendMessage());
    } else if (ev.key === 'ArrowUp' && atTheBeginning) {
        // Search for the previous human message from the index historyIndexHumanMsg
        if (historyIndexHumanMsg === -1)
            historyIndexHumanMsg = store.messages.length
        ev.preventDefault()
        if (store.messages) {
            for (let i = historyIndexHumanMsg - 1; i >= 0; i--) {
                if (store.messages[i].sender.type === 'human') {
                    chatInput.value.innerText = store.messages[i].stack[0].payload.content
                    historyIndexHumanMsg = i
                    break
                }
            }
        }
    } else if (ev.key === 'ArrowDown' && atTheEnd) { // Search for the next human message from the index historyIndexHumanMsg
        ev.preventDefault()
        if (historyIndexHumanMsg === -1)
            historyIndexHumanMsg = store.messages.length
        if (store.messages) {
            for (let i = historyIndexHumanMsg + 1; i < store.messages.length; i++) {
                if (store.messages[i].sender.type === 'human') {
                    chatInput.value.innerText = store.messages[i].stack[0].payload.content
                    historyIndexHumanMsg = i
                    break
                }
            }
        }
    }
}

function createSendMessage() {
    if (!store.promptWithText || !store.canSendMsg)
        return

    historyIndexHumanMsg = -1
    const user_message = chatInput.value.innerText.trim()
    const message = {
        "sender": {
            "type": "human",
            "platform": "WS",
        },
        "stack": [{
            "type": "message",
            "payload": {
                "content": user_message
            },
        }],
        "stack_id": "0",
        "stack_group_id": "0",
        "last": true,
    };
    if (store.userId !== undefined)
        message["sender"]["id"] = store.userId

    chatInput.value.innerText = "";
    store.promptWithText = false
    return message
}

</script>

<style scoped lang="scss">

.chat-prompt-wrapper {
    padding: 24px;
    display: flex;
    background-color: $chatfaq-color-chat-background-light;
    &.dark-mode {
        background-color: $chatfaq-color-chat-background-dark;
    }

    &.fit-to-parent-prompt {
        border-radius: inherit;
    }
    .chat-prompt-outer {
        width: 100%;
        display: flex;
        border-radius: 4px;
        border: 1px solid $chatfaq-color-chatInput-border-light !important;
        box-shadow: 0px 4px 4px $chatfaq-box-shadows-color;

        .attach-buttom {
            margin-top: auto;
            margin-bottom: auto;
            line-height: 100%;
            margin-left: 16px;
            cursor: pointer;
            color: $chatfaq-attach-icon-color-light;
            &.dark-mode {
                color: $chatfaq-attach-icon-color-dark;
            }

        }
    }

    &.stick-input-prompt {
        position: sticky;
        bottom: 0px;
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
            @include scroll-style($chatfaq-color-scrollBar-dark);
        }
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

        &.disabled {
            cursor: not-allowed;
            opacity: 0.6;
            pointer-events: none;
        }
    }
    .dark-mode[contenteditable][placeholder]:empty:before {
        color: $chatfaq-color-chatPlaceholder-text-dark;
    }

    [contenteditable][placeholder]:empty:before {
        content: attr(placeholder);
        position: absolute;
        color: $chatfaq-color-chatPlaceholder-text-light;
        background-color: transparent;
        font-style: italic;
        cursor: text;
    }
}

</style>
