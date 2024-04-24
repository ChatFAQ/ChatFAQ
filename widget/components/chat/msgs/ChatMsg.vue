<template>
    <div class="message-wrapper"
        :class="{
            [props.message.sender.type]: true,
            'is-first': props.isFirst,
            'is-last': props.isLast,
            'maximized': store.maximized
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
                class="stack-wrapper">
                <div class="stack"
                    :class="{
                        [props.message.sender.type]: true,
                        'dark-mode': store.darkMode,
                        'maximized': store.maximized,
                        'sources-first': store.sourcesFirst,
                        'feedbacking': feedbacking
                    }">
                    <div class="layer" v-for="layer in props.message.stack">
                        <TextMsg v-if="store.displayGeneration && layer.type === MSG_TYPES.text" :data="layer"/>
                        <LMMsg v-if="layer.type === MSG_TYPES.lm_generated_text" :data="layer" :is-last="isLastOfType && layersFinished"/>
                    </div>
                    <References v-if="store.displaySources && props.message.stack && props.message.stack[0].payload?.references?.knowledge_items?.length && isLastOfType && (layersFinished || store.sourcesFirst)" :references="props.message.stack[0].payload.references"></References>
                </div>
                <UserFeedback
                    v-if="
                        props.message.sender.type === 'bot' &&
                        props.message.stack[props.message.stack.length - 1].meta &&
                        props.message.stack[props.message.stack.length - 1].meta.allow_feedback &&
                        props.message.last
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
import {useGlobalStore} from "~/store";
import UserFeedback from "~/components/chat/UserFeedback.vue";
import TextMsg from "~/components/chat/msgs/text/TextMsg.vue";
import LMMsg from "~/components/chat/msgs/llm/LMMsg.vue";
import References from "~/components/chat/msgs/llm/References.vue";
import {ref, computed} from "vue";

const props = defineProps(["message", "isLast", "isLastOfType", "isFirst"]);
const store = useGlobalStore();
const feedbacking = ref(null)

const MSG_TYPES = {
    text: "text",
    lm_generated_text: "lm_generated_text",
}
const layersFinished = computed(() =>  props.message.last)

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
                margin-right: 35vw;
            }
        }
    }

    &.human {
        margin-right: 24px;
        margin-left: 86px;

        &.maximized {
            @media only screen and (min-width: $phone-breakpoint) {
                margin-left: 35vw;
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
        margin: 16px 0 0;

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
}

.stack-wrapper {
    max-width: 100%;

    .stack {
        max-width: 100%;
        border-radius: 6px;
        padding: 9px 15px 9px 15px;
        word-wrap: break-word;

        &.bot {
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

        &.human {
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
</style>
