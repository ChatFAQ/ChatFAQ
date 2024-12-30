<template>
    <div class="text-feedback-wrapper">
        <div class="content">{{ props.data.content }}</div>
        <div v-if="!feedbackSent">
            <div class="feedback-input-wrapper" :class="{ 'dark-mode': store.darkMode }">
                <div
                    :placeholder="props.data.hint || $t('typeyourfeedback')"
                    class="feedback-input"
                    :class="{ 'dark-mode': store.darkMode }"
                    ref="feedbackInput"
                    @keydown="(ev) => manageEnterInput(ev, () => sendFeedback())"
                    contenteditable
                    oninput="if(this.innerHTML.trim()==='<br>')this.innerHTML=''"
                />
            </div>
            <div class="submit-feedback-wrapper">
                <div
                    @click="sendFeedback()"
                    :class="{ 'dark-mode': store.darkMode }"
                    >{{ $t('submitfeedback') }}</div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import { useGlobalStore } from "~/store";
import { useI18n } from 'vue-i18n';

const store = useGlobalStore();
const { t } = useI18n();
const feedbackInput = ref(null);
const feedbackSent = ref(false);

const props = defineProps({
    data: {
        type: Object,
        required: true,
    },
});

function manageEnterInput(ev, cb) {
    if (ev.key === 'Enter' && !ev.shiftKey) {
        ev.preventDefault();
        cb();
    }
}

function sendFeedback() {
    if (feedbackSent.value || !feedbackInput.value) return;
    
    const feedback = feedbackInput.value.innerText.trim();
    if (!feedback) return;

    console.log(feedback);

    // TODO: send feedback
    feedbackSent.value = true;
}
</script>

<style scoped lang="scss">
.text-feedback-wrapper {
    display: flex;
    flex-direction: column;
    gap: 8px;
    width: 570px;
    max-width: 100%;

    .content {
        line-height: 1.4;
        width: 100%;
    }

    .feedback-input-wrapper {
        margin: 12px 0;
        display: flex;
        width: 100%;
        border-radius: 4px;
        border: 1px solid $chatfaq-color-chatInput-border-light !important;
        background-color: $chatfaq-color-chat-background-light;
        box-shadow: 0px 4px 4px $chatfaq-box-shadows-color;
        align-self: stretch;

        &.dark-mode {
            background-color: $chatfaq-color-chat-background-dark;
        }

        .feedback-input {
            width: 100%;
            min-height: 80px;
            border: 0;
            outline: 0;
            margin: 10px 16px;
            background-color: $chatfaq-color-chat-background-light;
            word-wrap: break-word;
            max-height: 200px;
            font: $chatfaq-font-caption-md;
            font-style: normal;
            overflow-x: hidden;
            overflow-y: auto;

            @include scroll-style();

            &.dark-mode {
                @include scroll-style($chatfaq-color-scrollBar-dark);
                background-color: $chatfaq-color-chat-background-dark;
                color: $chatfaq-color-chat-background-light;

                &::placeholder {
                    color: $chatfaq-color-chatPlaceholder-text-dark;
                }
            }

        }

        [contenteditable][placeholder]:empty:before {
            content: attr(placeholder);
            color: $chatfaq-color-chatPlaceholder-text-light;
            background-color: transparent;
            font-style: italic;
            cursor: text;
        }

        .dark-mode[contenteditable][placeholder]:empty:before {
            color: $chatfaq-color-chatPlaceholder-text-dark;
        }
    }

    .submit-feedback-wrapper {
        div {
            float: right;
            padding: 8px 16px;
            color: $chatfaq-color-chatMessageHuman-background-light;
            border-radius: 24px;
            font-weight: 700;
            cursor: pointer;
            font-size: 14px;
            font-style: normal;
            line-height: 20px;
            text-decoration: underline solid;
            text-underline-offset: 4px;
            -webkit-tap-highlight-color: transparent;
            transition: opacity 0.2s ease;

            &:hover {
                opacity: 0.7;
            }

            &.dark-mode {
                color: $chatfaq-color-chatMessageHuman-background-dark;
            }
        }
    }
}
</style>