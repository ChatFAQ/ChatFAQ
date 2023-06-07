<template>
    <div class="message-wrapper"
        :class="{
            [props.data.sender.type]: true,
            'is-first-of-type': props.isFirstOfType,
            'is-first': props.isFirst,
            'is-last': props.isLast,
            'maximized': store.maximized
        }">
        <div
            class="message"
            :class="{
                [props.data.sender.type]: true,
                'is-first-of-type': props.isFirstOfType,
                'is-first': props.isFirst,
                'is-last': props.isLast,
                'maximized': store.maximized
            }">
            <div class="content"
                 v-if="props.data.type === MSG_TYPES.text || props.data.type === MSG_TYPES.lm_generated_text"
                 :class="{
                [props.data.sender.type]: true,
                'is-last-of-type': props.isLastOfType,
                'dark-mode': store.darkMode,
                'maximized': store.maximized,
                'feedbacked': feedbacked,
            }">{{ props.data.payload }}
            </div>
            <UserFeedback
                v-if="props.isLastOfType && props.data.sender.type === 'bot' && props.data.meta.allow_feedback"
                :msg-id="data.id"
                @feedbacked="feedbacked = true"
                @collapse="feedbacked = false"
            ></UserFeedback>
        </div>
    </div>
</template>

<script setup>
import {useGlobalStore} from "~/store";
import UserFeedback from "~/components/chat/UserFeedback.vue";

const props = defineProps(["data", "isLastOfType", "isFirstOfType", "isLast", "isFirst"]);
const store = useGlobalStore();
const feedbacked = ref(null)

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

        &.feedbacked {
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
</style>
