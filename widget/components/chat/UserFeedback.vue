<template>
    <div class="voting"
         :class="{'feedbacked': feedbacked && !collapse, 'dark-mode': store.darkMode}">
        <div class="separator-line" v-if="feedbacked && !collapse" :class="{ 'dark-mode': store.darkMode }"></div>
        <div class="feedback-top">
            <div class="feedback-top-text" v-if="feedbacked && !collapse">{{ $t('additionalfeedback') }}</div>
            <!-- <div v-else-if="feedbacked">{{ $t('feedbacksent') }}:</div> -->
            <div class="feedback-controls">
                <ThumbUp class="control" :class="{'selected': feedbackValue === 'positive', 'dark-mode': store.darkMode, 'collapse': collapse}" @click="sendUserFeedback('positive')" />
                <ThumbDown class="control" :class="{'selected': feedbackValue === 'negative', 'dark-mode': store.darkMode, 'collapse': collapse}" @click="sendUserFeedback('negative')"/>
                <CopyToClipboard :msg-id="msgId"/>
            </div>
        </div>
        <div v-if="feedbacked && !collapse">
            <div class="feedback-input-wrapper" :class="{ 'dark-mode': store.darkMode }">
                <div
                    v-if="feedbackValue === 'negative'"
                    :placeholder="$t('whatwastheissue')"
                    class="feedback-input"
                    :class="{ 'dark-mode': store.darkMode }"
                    ref="feedbackInput"
                    @keydown="(ev) => manageEnterInput(ev, () => sendUserFeedback(feedbackValue, true))"
                    contenteditable
                    oninput="if(this.innerHTML.trim()==='<br>')this.innerHTML=''"
                />
                <div
                    v-else
                    :placeholder="$t('whatdidyoulike')"
                    class="feedback-input"
                    :class="{ 'dark-mode': store.darkMode }"
                    ref="feedbackInput"
                    @keydown="(ev) => manageEnterInput(ev, () => sendUserFeedback(feedbackValue, true))"
                    contenteditable
                    oninput="if(this.innerHTML.trim()==='<br>')this.innerHTML=''"
                />
            </div>
            <div class="quick-responses" v-if="feedbackValue === 'negative'">
                <div class="quick-response" @click="quickAnswer1 = !quickAnswer1">
                    <Checkbox v-model="quickAnswer1" :dark="true" :not-reactive="true"/>
                    <span>{{ $t("reason1") }}</span>
                </div>
                <div class="quick-response" @click="quickAnswer2 = !quickAnswer2">
                    <Checkbox v-model="quickAnswer2" :dark="true" :not-reactive="true"/>
                    <span>{{ $t("reason2") }}</span>
                </div>
                <div class="quick-response" @click="quickAnswer3 = !quickAnswer3">
                    <Checkbox v-model="quickAnswer3" :dark="true" :not-reactive="true"/>
                    <span>{{ $t("reason3") }}</span>
                </div>
            </div>
            <div class="submit-feedback-wrapper">
                <div
                    @click="sendUserFeedback(feedbackValue, true)"
                    :class="{ 'dark-mode': store.darkMode }"
                > {{ $t('submitfeedback') }}</div>
            </div>
        </div>
    </div>
</template>

<script setup>
import {useGlobalStore} from "~/store";
import Checkbox from "~/components/generic/Checkbox.vue";
import {useI18n} from 'vue-i18n'
import CopyToClipboard from "~/components/chat/CopyToClipboard.vue";
import {ref, defineProps, onMounted} from "vue";
import ThumbUp from "~/components/icons/ThumbUp.vue";
import ThumbDown from "~/components/icons/ThumbDown.vue";

const props = defineProps(["msgId"]);

const store = useGlobalStore();
const feedbacked = ref(null)
const feedbackInput = ref(null);
const collapse = ref(false)
const feedbackValue = ref(null)
const quickAnswer1 = ref(false);
const quickAnswer2 = ref(false);
const quickAnswer3 = ref(false);
const emit = defineEmits(['feedbacking', 'collapse'])
const {t} = useI18n()

function manageEnterInput(ev, cb) {
    if (ev.key === 'Enter' && !ev.shiftKey) {
        ev.preventDefault()
        cb();
    }
};

onMounted(async () => {
    if (store.previewMode)
        return

    let response = await fetch(
        store.chatfaqAPI + `/back/api/broker/user-feedback/?message=${props.msgId}`, { headers: {
            Authorization: `Token ${store.authToken}`
        }}
    )
    response = await response.json();
    if (response.results && response.results.length) {
        const userFeedback = response.results[0]
        collapse.value = true
        feedbackValue.value = userFeedback.value
    }
})

async function sendUserFeedback(value, _collapse) {
    if (store.previewMode)
        return

    if (collapse.value)
        return
    feedbackValue.value = value

    const feedbackData = {
        message: props.msgId,
        value: value,
    };
    if (feedbackInput.value) {
        const feedback = feedbackInput.value.innerText.trim()
        if (feedback)
            feedbackData["feedback_comment"] = feedback
    }
    feedbackData["feedback_selection"] = []
    if (quickAnswer1.value)
        feedbackData["feedback_selection"] = [...feedbackData["feedback_selection"], t("reason1")]
    if (quickAnswer2.value)
        feedbackData["feedback_selection"] = [...feedbackData["feedback_selection"], t("reason2")]
    if (quickAnswer3.value)
        feedbackData["feedback_selection"] = [...feedbackData["feedback_selection"], t("reason3")]

    let method = "POST"
    let endpoint = '/back/api/broker/user-feedback/'
    if (feedbacked.value) {
        feedbackData["id"] = feedbacked.value
        method = "PATCH"
        endpoint = `${endpoint}${feedbackData["id"]}/`
    }
    const response = await fetch(store.chatfaqAPI + endpoint, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Token ${store.authToken}`
        },
        body: JSON.stringify(feedbackData)
    })

    const res = await response.json();
    feedbacked.value = res["id"]
    emit('feedbacking')
    if (_collapse) {
        collapse.value = true
        emit("collapse")
        store.feedbackSent += 1;
    }
    store.scrollToBottom += 1;
}

</script>
<style scoped lang="scss">

.voting {
    width: 100%;
    display: flex;
    flex-direction: column;
    border-radius: 0px 0px 6px 6px;


    &.feedbacked {
        background-color: $chatfaq-color-chatMessageBot-background-light;
        &.dark-mode {
            background-color: $chatfaq-color-chatMessageBot-background-dark !important;
            color: $chatfaq-color-chatMessageBot-text-dark !important;
        }
    }

    .feedback-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
        .feedback-top-text {
            margin-left: 15px;
        }
        .feedback-controls {
            margin-right: 10px;
            display: flex;
            margin-left: auto;
            > svg {
               margin-right: 6px;
            }
        }
    }

    .separator-line {
        height: 1px;
        background-color: $chatfaq-color-separator-light;
        align-content: center;
        text-align: center;
        margin: 15px;
        margin-top: 0px;
        margin-bottom: 8px;
        &.dark-mode {
            background-color: $chatfaq-color-separator-dark;
        }
    }

    .feedback-input-wrapper {
        margin: 12px;
        display: flex;
        border-radius: 4px;
        border: 1px solid $chatfaq-color-chatInput-border-light !important;
        background-color: $chatfaq-color-chat-background-light;
        box-shadow: 0px 4px 4px $chatfaq-box-shadows-color;
        font-weight: 400;

        &.dark-mode {
            background-color: $chatfaq-color-chat-background-dark;
        }

        .feedback-input, .feedback-input:focus, .feedback-input:hover {
            width: 100%;
            border: 0;
            outline: 0;
            margin-left: 16px;
            background-color: $chatfaq-color-chat-background-light;

            @include scroll-style();

            &.dark-mode {
                @include scroll-style($chatfaq-color-scrollBar-dark);
            }
        }


        .feedback-input {
            word-wrap: break-word;
            padding: 0px;
            max-height: 35px;
            margin-bottom: 10px;
            margin-top: 10px;
            font: $chatfaq-font-caption-md;
            font-style: normal;
            overflow-x: hidden;
            overflow-y: auto;

            &::placeholder {
                font-style: italic;
                color: $chatfaq-color-chatInput-text-light;
                letter-spacing: -0.5px;
                font-style: italic;
                font-weight: 400;
            }

            &.dark-mode {
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

    .selected, .control:not(.collapse):hover {
        color: $chatfaq-color-chatMessageReference-text-light;
        background: rgba(70, 48, 117, 0.1);
        border-radius: 2px;
        &.dark-mode {
            background-color: $chatfaq-color-chatMessageReference-background-dark;
            color: $chatfaq-color-chatMessageReference-text-dark;
        }
    }

    .quick-responses {
        margin-left: 15px;

        .quick-response {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            cursor: pointer;

            > span {
                margin-left: 6px;
            }
        }
    }

    .submit-feedback-wrapper {
        div {
            float: right;
            padding: 8px 16px;
            background: $chatfaq-color-chatMessageHuman-background-light;
            border-radius: 24px;
            margin-bottom: 16px;
            margin-right: 12px;
            color: white;
            font-weight: 600;
            cursor: pointer;
            text-transform: uppercase;
            font-size: 12px;
            font-style: normal;

            &.dark-mode {
                background-color: $chatfaq-color-chatMessageHuman-background-dark;
            }
        }
    }
}

</style>
