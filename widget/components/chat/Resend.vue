<template>
    <div class="resend" :class="{'dark-mode': store.darkMode}">
        <div class="feedback-top">
            <div class="feedback-top-text" v-if="feedbacked && !collapse">{{ $t('additionalfeedback') }}</div>
            <div class="feedback-controls">
                <ThumbUp class="control" :class="{'dark-mode': store.darkMode}" @click="resendMsg" />
            </div>
        </div>
    </div>
</template>

<script setup>
import {useGlobalStore} from "~/store";
import {useI18n} from 'vue-i18n'
import {defineProps} from "vue";
import ThumbUp from "~/components/icons/ThumbUp.vue";
const props = defineProps(["msgId"]);

const store = useGlobalStore();
const {t} = useI18n()


async function resendMsg(value, _collapse) {
    if (store.previewMode)
        return

    store.resendMsgId = props.msgId
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
        &.collapse {
            cursor: unset;
        }

    }
}

</style>
