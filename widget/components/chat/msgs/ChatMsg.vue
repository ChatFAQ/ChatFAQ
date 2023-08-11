<template>
    <div class="message-wrapper"
        :class="{
            [props.layers[0].sender.type]: true,
            'is-first-of-type': props.isFirstOfType,
            'is-first': props.isFirst,
            'is-last': props.isLast,
            'maximized': store.maximized
        }">
        <div
            class="message"
            :class="{
                [props.layers[0].sender.type]: true,
                'is-first': props.isFirst,
                'is-last': props.isLast,
                'maximized': store.maximized
            }">
            <div
                class="stack-wrapper">
                <div class="stack"
                    :class="{
                        [props.layers[props.layers.length - 1].sender.type]: true,
                        'dark-mode': store.darkMode,
                        'maximized': store.maximized,
                        'feedbacking': feedbacking
                    }">
                    <div class="layer" v-for="layer in props.layers">
                        <TextMsg v-if="layer.type === MSG_TYPES.text" :data="layer"/>
                        <LMMsg v-if="layer.type === MSG_TYPES.lm_generated_text" :data="layer"/>
                    </div>
                    <References v-if="props.references.length" :references="props.references"></References>
                </div>
                <UserFeedback
                    v-if="
                        props.layers[0].sender.type === 'bot' &&
                        props.layers[props.layers.length - 1].meta.allow_feedback &&
                        props.layers[props.layers.length - 1].last
                    "
                    :msg-id="props.layers[props.layers.length - 1].id"
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
import {ref} from "vue";

const props = defineProps(["layers", "references", "isFirstOfType", "isLast", "isFirst"]);
const store = useGlobalStore();
const feedbacking = ref(null)

const MSG_TYPES = {
    text: "text",
    lm_generated_text: "lm_generated_text",
}


</script>
<style scoped lang="scss">
@import "assets/styles/variables";
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
            background-color: $chatfaq-color-primary-300;
            color: $chatfaq-color-neutral-black;

            &.dark-mode {
                background-color: $chatfaq-color-primary-800;
                color: $chatfaq-color-neutral-white;
            }
        }

        &.human {
            border: none;
            background-color: $chatfaq-color-primary-500;
            color: $chatfaq-color-neutral-white;

            &.dark-mode {
                background-color: $chatfaq-color-primary-900;
                color: $chatfaq-color-neutral-white;
            }
        }

        &.feedbacking {
            border-radius: 6px 6px 0px 0px !important;
            min-width: 100%;
        }
    }

    .message {
        display: flex;
        align-items: baseline;
        flex-direction: column;
        max-width: 100%;
        height: 100%;
        margin: 8px 0px 0px;


        &.is-first-of-type {
            margin-top: 16px;
        }

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
            background-color: $chatfaq-color-primary-300;
            color: $chatfaq-color-neutral-black;

            &.dark-mode {
                background-color: $chatfaq-color-primary-800;
                color: $chatfaq-color-neutral-white;
            }

            &.is-last-of-type {
                border-radius: 6px 6px 6px 0px;
            }
        }

        &.human {
            border: none;
            background-color: $chatfaq-color-primary-500;
            color: $chatfaq-color-neutral-white;

            &.dark-mode {
                background-color: $chatfaq-color-primary-900;
                color: $chatfaq-color-neutral-white;
            }

            &.is-last-of-type {
                border-radius: 6px 6px 0px 6px;
            }
        }

        &.feedbacking {
            border-radius: 6px 6px 0px 0px !important;
            min-width: 100%;
        }
        .layer:not(:last-child) {
            margin-bottom: 5px;
        }
    }
}
</style>
