<template>
    <div class="message-wrapper"
         :class="{
            [props.message.sender.type]: true,
            'is-first': props.isFirst,
            'is-last': props.isLast,
            'maximized': store.maximized,
            'mobile-no-margins': iframedMsg && iframedMsg.mobileNoMargins,
            'desktop-no-margins': iframedMsg && iframedMsg.desktopNoMargins,
        }">
        <div
            class="message"
            :class="{
                [props.message.sender.type]: true,
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
                        [props.message.sender.type]: true,
                        'dark-mode': store.darkMode,
                        'maximized': store.maximized,
                        'sources-first': store.sourcesFirst,
                        'feedbacking': feedbacking,
                        'full-width': iframedMsg && iframedMsg.fullWidth,
                        'no-padding': iframedMsg && iframedMsg.noPadding,
                        'backgrounded': getFirstStackType() !== 'file_download',
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
                    <template v-if="getFirstStackType() === 'message'">
                        <div class="layer" v-for="layer in props.message.stack">
                            <Message :data="layer" :is-last="isLastOfType && layersFinished" />
                        </div>
                        <References
                            v-if="!store.hideSources && props.message.stack && props.message.stack[0].payload?.references?.knowledge_items?.length && isLastOfType && (layersFinished || store.sourcesFirst)"
                            :references="props.message.stack[0].payload.references"></References>
                    </template>
                    <template v-else-if="getFirstStackType() === 'file_upload'">
                        <div class="layer" v-for="layer in props.message.stack">
                            <FileUpload :data="layer.payload" />
                        </div>
                    </template>
                    <template v-else-if="getFirstStackType() === 'file_download'">
                        <div class="layer" v-for="layer in props.message.stack">
                            <FileDownload :data="layer.payload" />
                        </div>
                    </template>
                    <template v-else>
                        <div class="layer">
                            <span>Stack type not supported</span>
                        </div>
                    </template>
                </div>
                <UserFeedback
                    v-if="
                        props.message.sender.type === 'bot' &&
                        props.message.stack[props.message.stack.length - 1].meta &&
                        props.message.stack[props.message.stack.length - 1].meta.allow_feedback &&
                        props.message.last_chunk
                    "
                    :msgId="props.message.id"
                    @feedbacking="feedbacking = true"
                    @collapse="feedbacking = false"
                ></UserFeedback>
            </div>
        </div>
    </div>
</template>

<script setup>
import { useGlobalStore } from "~/store";
import UserFeedback from "~/components/chat/UserFeedback.vue";
import Message from "~/components/chat/msgs/Message.vue";
import References from "~/components/chat/msgs/References.vue";
import {ref, computed, onMounted, onBeforeUnmount, watch} from "vue";
import FileDownload from "~/components/chat/msgs/FileDownload.vue";
import FileUpload from "~/components/chat/msgs/FileUpload.vue";

const props = defineProps(["message", "isLast", "isLastOfType", "isFirst"]);
const store = useGlobalStore();
const feedbacking = ref(null);
const iframeHeight = ref(40);

const layersFinished = computed(() => props.message.last);
const iframedWindow = ref(null);
const iframedMsg = computed(() => store.customIFramedMsg(getFirstStackType()));


const emit = defineEmits(['s3Path']);


function getFirstStackType() {
    return props.message.stack[0].type;
}
function addingQueryParamStack(url) {
    if (!url) return;
    const urlObj = new URL(url);
    urlObj.searchParams.set("stack", JSON.stringify(props.message.stack));
    return urlObj.toString();
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
