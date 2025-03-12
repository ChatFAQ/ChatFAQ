<template>
    <div class="resend" :class="{'dark-mode': store.darkMode}">
        <div class="feedback-top">
            <div class="feedback-controls">
                <Repeat class="control" :class="{'dark-mode': store.darkMode}" @click="resendMsg" />
            </div>
        </div>
    </div>
</template>

<script setup>
import {useGlobalStore} from "~/store";
import {useI18n} from 'vue-i18n'
import {defineProps, nextTick} from "vue";
import Repeat from "~/components/icons/Repeat.vue";
const props = defineProps(["msgId"]);

const store = useGlobalStore();
const {t} = useI18n()


async function resendMsg(value, _collapse) {
    if (store.previewMode)
        return
    store.resendMsgId = undefined;
    await nextTick(() => {
        store.resendMsgId = props.msgId;
    })
}

</script>
<style scoped lang="scss">

.resend {
    width: 100%;
    display: flex;
    flex-direction: column;
    border-radius: 0px 0px 6px 6px;


    .feedback-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
        .feedback-top-text {
            margin-left: 15px;
        }
        .feedback-controls {
            display: flex;
            margin-left: auto;
            > svg {
               margin-right: 6px;
            }
        }
    }

    .control {
        cursor: pointer;
        color: $chatfaq-color-thumbs-and-clipboard-light;
        margin-top: 7px;
        display: flex;
        div {
            svg {
                margin-right: 10px;
            }
        }
        &.dark-mode {
            color: $chatfaq-color-thumbs-and-clipboard-dark;
        }
        &:hover {
            color: $chatfaq-color-chatMessageReference-text-light;
            background: rgba(70, 48, 117, 0.1);
            border-radius: 2px;
            &.dark-mode {
                background-color: $chatfaq-color-chatMessageReference-background-dark;
                color: $chatfaq-color-chatMessageReference-text-dark;
            }
        }
    }
}

</style>
