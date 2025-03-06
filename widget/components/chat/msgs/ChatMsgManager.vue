<template>
    <div class="message-wrapper"
         :class="{
            [getMessageType()]: true,
            'is-first': props.isFirst,
            'is-last': props.isLast,
            'maximized': store.maximized,
            'mobile-no-margins': iframedMsg && iframedMsg.mobileNoMargins,
            'desktop-no-margins': iframedMsg && iframedMsg.desktopNoMargins,
            'hidden': shouldHideMessage()
        }">
        <div
            class="message"
            :class="{
                [getMessageType()]: true,
                'is-first': props.isFirst,
                'is-last': props.isLast,
                'maximized': store.maximized
            }">
            <div
                class="stack-wrapper"
                :class="{
                    'full-width': iframedMsg && iframedMsg.fullWidth,
                }">
                <div class="stack"
                     :class="{
                        [getMessageType()]: true,
                        'dark-mode': store.darkMode,
                        'maximized': store.maximized,
                        'sources-first': store.sourcesFirst,
                        'feedbacking': feedbacking,
                        'full-width': iframedMsg && iframedMsg.fullWidth,
                        'no-padding': iframedMsg && iframedMsg.noPadding,
                        'backgrounded': getFirstLayerType() !== 'file_uploaded',
                    }"
                    :style="{
                        height: iframedMsg ? iframeHeight + 'px' : undefined,
                    }"
                >
                    <template v-if="iframedMsg">
                        <iframe
                            ref="iframedWindow"
                            style="border: 0;"
                            :style="{
                                height: iframeHeight + 'px',
                            }"
                            :src="addingQueryParamStack(iframedMsg.src)"
                            :class="{
                                'full-width': iframedMsg.fullWidth,
                            }"
                            :scrolling="iframedMsg.scrolling || 'auto'"
                        ></iframe>
                    </template>
                    <template v-else-if="getFirstLayerType() === 'message' || getFirstLayerType() === 'message_chunk'">
                        <div class="layer" v-for="layer in props.message.stack">
                            <TextMsgPiece :data="layer" :is-last="isLastOfType && layersFinished" :is-last-chunk="stackFinished"/>
                        </div>
                        <ReferencesMsgPiece
                            v-if="!store.hideSources && props.message.stack && props.message.stack[0].payload?.references?.knowledge_items?.length && (stackFinished || store.sourcesFirst)"
                            :references="props.message.stack[0].payload.references"
                        ></ReferencesMsgPiece>
                    </template>
                    <template v-else-if="getFirstLayerType() === 'tool_use' && !store.hideToolMessages">
                        <div class="layer" v-for="layer in props.message.stack">
                            <TextMsgPiece
                                :data="formatToolUseLayer(layer)"
                                :is-last="isLastOfType && layersFinished"
                                :is-last-chunk="stackFinished"
                            />
                        </div>
                    </template>
                    <template v-else-if="getFirstLayerType() === 'tool_result' && !store.hideToolMessages">
                        <div class="layer" v-for="layer in props.message.stack">
                            <TextMsgPiece
                                :data="formatToolResultLayer(layer)"
                                :is-last="isLastOfType && layersFinished"
                                :is-last-chunk="stackFinished"
                            />
                        </div>
                    </template>
                    <template v-else-if="getFirstLayerType() === 'file_upload'">
                        <div class="layer" v-for="layer in props.message.stack">
                            <FileUploadMsgPiece :data="layer.payload" />
                        </div>
                    </template>
                    <template v-else-if="getFirstLayerType() === 'file_uploaded'">
                        <div class="layer" v-for="layer in props.message.stack">
                            <AttachmentMsgPiece :data="layer.payload" />
                        </div>
                    </template>
                    <template v-else-if="getFirstLayerType() === 'file_download'">
                        <div class="layer" v-for="layer in props.message.stack">
                            <AttachmentMsgPiece :data="layer.payload" />
                        </div>
                    </template>
                    <template v-else-if="getFirstLayerType() === 'star_rating'">
                        <div class="layer" v-for="layer in props.message.stack">
                            <Teleport v-if="getFirstLayerMergeToPrev()" :to="'#msg-commands-' + store.getPrevMsg(props.message, messageIsNotFeedback).id">
                                <StarRatingMsgPiece :data="layer.payload" :msgId="props.message.id" :msgTargetId="store.getPrevMsg(props.message, messageIsNotFeedback).id" />
                            </Teleport>
                            <StarRatingMsgPiece v-else :data="layer.payload" :msgId="props.message.id" :msgTargetId="store.getPrevMsg(props.message, messageIsNotFeedback).id" />
                        </div>
                    </template>
                    <template v-else-if="getFirstLayerType() === 'text_feedback'">
                        <div class="layer" v-for="layer in props.message.stack">
                            <Teleport v-if="getFirstLayerMergeToPrev()" :to="'#msg-commands-' + store.getPrevMsg(props.message, messageIsNotFeedback).id">
                                <TextFeedbackMsgPiece :data="layer.payload" :msgId="props.message.id" :msgTargetId="store.getPrevMsg(props.message, messageIsNotFeedback).id" />
                            </Teleport>
                            <TextFeedbackMsgPiece v-else :data="layer.payload" :msgId="props.message.id" :msgTargetId="store.getPrevMsg(props.message, messageIsNotFeedback).id" />
                        </div>
                    </template>
                    <template v-else-if="getFirstLayerType() === 'thumbs_rating'">
                        <div class="layer" v-for="layer in props.message.stack">
                            <Teleport v-if="getFirstLayerMergeToPrev()" :to="'#msg-commands-' + store.getPrevMsg(props.message, messageIsNotFeedback).id">
                                <UserFeedback :msgId="props.message.id" :msgTargetId="store.getPrevMsg(props.message, messageIsNotFeedback).id" @feedbacking="feedbacking = true" @disabled="feedbacking = false"/>
                            </Teleport>
                            <UserFeedback v-else :msgId="props.message.id" :msgTargetId="store.getPrevMsg(props.message, messageIsNotFeedback).id" @feedbacking="feedbacking = true" @disabled="feedbacking = false"/>
                        </div>
                    </template>
                    <template v-else>
                        <div class="layer">
                            <span>Stack type not supported</span>
                        </div>
                    </template>
                </div>
                <div class="msg-commands" :id="'msg-commands-' + props.message.id">
                    <Resend
                        v-if="
                            props.message.sender.type === 'human' &&
                            store.enableResend
                        "
                        :msgId="store.getPrevMsg(props.message).id"
                    ></Resend>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { useGlobalStore } from "~/store";
import UserFeedback from "~/components/chat/msgs/pieces/UserFeedback.vue";
import Resend from "~/components/chat/Resend.vue";
import ReferencesMsgPiece from "~/components/chat/msgs/pieces/ReferencesMsgPiece.vue";
import {ref, computed, onMounted, onBeforeUnmount, watch} from "vue";
import TextMsgPiece from "~/components/chat/msgs/pieces/TextMsgPiece.vue";
import AttachmentMsgPiece from "~/components/chat/msgs/pieces/AttachmentMsgPiece.vue";
import FileUploadMsgPiece from "~/components/chat/msgs/pieces/FileUploadMsgPiece.vue";
import StarRatingMsgPiece from "~/components/chat/msgs/pieces/StarRatingMsgPiece.vue";
import TextFeedbackMsgPiece from "~/components/chat/msgs/pieces/TextFeedbackMsgPiece.vue";

const props = defineProps(["message", "isLast", "isLastOfType", "isFirst"]);
const store = useGlobalStore();
const feedbacking = ref(null);
const iframeHeight = ref(40);

const layersFinished = computed(() => props.message.last);
const stackFinished = computed(() => props.message.last_chunk);
const iframedWindow = ref(null);
const iframedMsg = computed(() => store.customIFramedMsg(getFirstLayerType()));


const emit = defineEmits(['s3Path']);


function getFirstLayerType() {
    return props.message.stack[0].type;
}
function getFirstLayerMergeToPrev() {
    return props.message?.stack[0]?.payload.merge_to_prev;
}
function messageIsNotFeedback(message) {
    return !message.stack.some(layer => ['text_feedback', 'star_rating', 'thumbs_rating'].includes(layer.type));
}
function addingQueryParamStack(url) {
    if (!url) return;
    const urlObj = new URL(url, window.location.origin);
    urlObj.searchParams.set("stack", JSON.stringify(props.message.stack));
    return urlObj.toString();
}

function shouldHideMessage() {
    if (!store.hideToolMessages) return false;
    const messageType = getFirstLayerType();
    return messageType === 'tool_use' || messageType === 'tool_result';
}

onMounted(() => {
    window.addEventListener('message', handleMessage);
});

onBeforeUnmount(() => {
    window.removeEventListener('message', handleMessage);
});

function handleMessage(event) {
    if (iframedWindow.value && event.source === iframedWindow.value.contentWindow) {
        iframeHeight.value = event.data;
    }
}

watch(() => store.maximized, () => {
    if (iframedWindow.value) {
        iframedWindow.value.contentWindow.postMessage('heightRequest', '*');
    }
});

function formatToolUseLayer(layer) {
    return {
        ...layer,
        payload: {
            content: `Tool ${layer.payload.name} called with args ${JSON.stringify(layer.payload.args)}`
        }
    };
}

function formatToolResultLayer(layer) {
    return {
        ...layer,
        payload: {
            content: `Tool result for ${layer.payload.name}: ${JSON.stringify(layer.payload.result, null, 2)}`
        }
    };
}

function getMessageType() {
    if (getFirstLayerType() === 'tool_result') {
        return 'bot';
    }
    return props.message.sender.type;
}

</script>
<style scoped lang="scss">
$phone-breakpoint: 600px;

.message-wrapper {
    display: flex;
    flex-direction: column;
    &.bot {
        margin-left: 24px;
        margin-right: 86px;

        &.maximized {
            @media only screen and (min-width: $phone-breakpoint) {
                // margin-right: 35vw;
            }
        }
    }

    &.human {
        margin-right: 24px;
        margin-left: 86px;

        &.maximized {
            @media only screen and (min-width: $phone-breakpoint) {
                // margin-left: 35vw;
            }
        }
    }

    &.hidden {
        display: none;
    }

    .content {
        border-radius: 6px;
        padding: 9px 15px 9px 15px;
        word-wrap: break-word;
        max-width: 100%;

        &.bot {
            background-color: $chatfaq-color-chatMessageBot-background-light;
            color: $chatfaq-color-chatMessageBot-text-light;

            &.dark-mode {
                background-color: $chatfaq-color-chatMessageBot-background-dark;
                color: $chatfaq-color-chatMessageBot-text-dark;
            }
        }

        &.human {
            border: none;
            background-color: $chatfaq-color-chatMessageHuman-background-light;
            color: $chatfaq-color-chatMessageHuman-text-light;

            &.dark-mode {
                background-color: $chatfaq-color-chatMessageHuman-background-dark;
                color: $chatfaq-color-chatMessageHuman-text-dark;
            }
        }

        &.feedbacking {
            border-radius: 6px 6px 0 0 !important;
            min-width: 100%;
        }
    }

    .message {
        display: flex;
        align-items: baseline;
        flex-direction: column;
        max-width: 570px;
        height: 100%;
        margin: $chatfaq-size-space-between-msgs 0 0;

        &.is-first {
            margin-top: 30px;
        }

        &.is-last {
            margin-bottom: 20px;
        }

        &.human {
            align-self: end;
        }
    }

    &.mobile-no-margins {
        @media only screen and (max-width: $phone-breakpoint) {
            margin-left: 5px;
            margin-right: 5px;
        }
    }
    &.desktop-no-margins {
        @media only screen and (min-width: $phone-breakpoint) {
            margin-left: 5px;
            margin-right: 5px;
        }
    }
    .msg-commands {
        display: flex;
        float: right;
    }
}

.stack-wrapper {
    max-width: 100%;

    .stack {
        max-width: 100%;
        border-radius: 6px;
        padding: 9px 15px 9px 15px;
        word-wrap: break-word;

        &.bot.backgrounded {
            background-color: $chatfaq-color-chatMessageBot-background-light;
            color: $chatfaq-color-chatMessageBot-text-light;

            &.dark-mode {
                background-color: $chatfaq-color-chatMessageBot-background-dark;
                color: $chatfaq-color-chatMessageBot-text-dark;
            }

            &.is-last-of-type {
                border-radius: 6px 6px 6px 0;
            }
        }

        &.human.backgrounded {
            border: none;
            background-color: $chatfaq-color-chatMessageHuman-background-light;
            color: $chatfaq-color-chatMessageHuman-text-light;

            &.dark-mode {
                background-color: $chatfaq-color-chatMessageHuman-background-dark;
                color: $chatfaq-color-chatMessageHuman-text-dark;
            }

            &.is-last-of-type {
                border-radius: 6px 6px 0 6px;
            }
        }

        &.feedbacking {
            border-radius: 6px 6px 0 0 !important;
            min-width: 100%;
        }

        &.sources-first {
            display: flex;
            flex-direction: column-reverse;
        }

        .layer:not(:last-child) {
            margin-bottom: 5px;
        }
    }
}

.full-width {
    width: 100% !important;
}
.no-padding {
    padding: 0 !important;
}

.file-uploaded-indicator {
    padding: 5px;

}
</style>
