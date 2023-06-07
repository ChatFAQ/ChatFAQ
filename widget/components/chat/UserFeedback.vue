<template>
    <div class="voting"
         :class="{'feedbacked': feedbacked && !collapse, 'dark-mode': store.darkMode}">
        <div class="separator-line" v-if="feedbacked && !collapse" :class="{ 'dark-mode': store.darkMode }"></div>
        <div class="feedback-top">
            <div class="feedback-top-text" v-if="feedbacked && !collapse">{{ $t('additionalfeedback') }}:</div>
            <!-- <div v-else-if="feedbacked">{{ $t('feedbacksent') }}:</div> -->
            <div class="feedback-controls">
                <!-- Thumb Up -->
                <div class="control" :class="{'selected': feedbackValue === 'positive', 'dark-mode': store.darkMode, 'collapse': collapse}">
                    <svg @click="userFeedback('positive')"
                         width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M2 7C2 6.44772 2.44772 6 3 6H4.66667V14H3C2.44772 14 2 13.5523 2 13V7Z"
                              stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        <path
                            d="M4.66669 7.33333V12.6667L5.65899 13.3282C6.31606 13.7662 7.08809 14 7.87779 14H10.1253C11.5918 14 12.8434 12.9398 13.0845 11.4932L13.6119 8.3288C13.8151 7.10973 12.875 6 11.6391 6H9.33335"
                            stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        <path
                            d="M9.33335 6L9.79147 3.70944C9.91061 3.11371 9.56752 2.5225 8.99117 2.33038V2.33038C8.42245 2.14081 7.80088 2.39827 7.53279 2.93447L5.33335 7.33333H4.66669"
                            stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>

                <!-- Thumb Down -->
                <div class="control" :class="{'selected': feedbackValue === 'negative', 'dark-mode': store.darkMode, 'collapse': collapse}">
                    <svg @click="userFeedback('negative')"
                         width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M14 9C14 9.55228 13.5523 10 13 10H11.3333V2H13C13.5523 2 14 2.44772 14 3V9Z"
                              stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        <path
                            d="M11.3333 8.66667V3.33333L10.341 2.6718C9.68394 2.23375 8.91191 2 8.12221 2H5.87469C4.40818 2 3.15661 3.06024 2.91551 4.5068L2.38811 7.6712C2.18494 8.89027 3.12502 10 4.3609 10H6.66665"
                            stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                        <path
                            d="M6.66665 10L6.20853 12.2906C6.08939 12.8863 6.43248 13.4775 7.00883 13.6696V13.6696C7.57755 13.8592 8.19912 13.6017 8.46721 13.0655L10.6666 8.66667H11.3333"
                            stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <!-- Copy -->
                <CopyToClipboard :msg-id="msgId"/>
            </div>
        </div>
        <div v-if="feedbacked && !collapse">
            <div class="feedback-input-wrapper" :class="{ 'dark-mode': store.darkMode }">
                <input
                    v-if="feedbackValue === 'negative'"
                    :placeholder="$t('whatwastheissue')"
                    v-model="feedback"
                    class="feedback-input"
                    :class="{ 'dark-mode': store.darkMode }"
                    ref="chatInput"
                    @keyup.enter="userFeedback(feedbackValue)"
                />
                <input
                    v-else
                    :placeholder="$t('whatdidyoulike')"
                    v-model="feedback"
                    class="feedback-input"
                    :class="{ 'dark-mode': store.darkMode }"
                    ref="chatInput"
                    @keyup.enter="userFeedback(feedbackValue)"
                />
            </div>
            <div class="quick-responses" v-if="feedbackValue === 'negative'">
                <div class="quick-response">
                    <Checkbox v-model="quickAnswer1" :dark="true"/>
                    <span>{{ $t("reason1") }}</span>
                </div>
                <div class="quick-response">
                    <Checkbox v-model="quickAnswer2" :dark="true"/>
                    <span>{{ $t("reason2") }}</span>
                </div>
                <div class="quick-response">
                    <Checkbox v-model="quickAnswer3" :dark="true"/>
                    <span>{{ $t("reason3") }}</span>
                </div>
            </div>
            <div class="submit-feedback-wrapper">
                <div
                    @click="userFeedback(feedbackValue, true)"
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

const props = defineProps(["msgId"]);

const store = useGlobalStore();
const feedbacked = ref(null)
const feedback = ref(null)
const collapse = ref(false)
const feedbackValue = ref(null)
const quickAnswer1 = ref(false);
const quickAnswer2 = ref(false);
const quickAnswer3 = ref(false);
const emit = defineEmits(['feedbacked', 'collapse'])
const {t} = useI18n()

async function userFeedback(value, _collapse) {
    if (collapse.value)
        return
    feedbackValue.value = value

    const feedbackData = {
        message: props.msgId,
        value: value,
        feedback: ""
    };
    if (feedback.value)
        feedbackData["feedback"] += feedback.value
    if (quickAnswer1.value)
        feedbackData["feedback"] += `${'\n' ? feedbackData["feedback"].length : ''}${t("reason1")}`
    if (quickAnswer2.value)
        feedbackData["feedback"] += `${'\n' ? feedbackData["feedback"].length : ''}${t("reason2")}`
    if (quickAnswer3.value)
        feedbackData["feedback"] += `${'\n' ? feedbackData["feedback"].length : ''}${t("reason3")}`

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
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(feedbackData)
    })

    const res = await response.json();
    feedbacked.value = res["id"]
    emit('feedbacked')
    if (_collapse) {
        collapse.value = true
        emit("collapse")
        store.feedbackSent += 1;
    }
    store.scrollToBottom += 1;
}

</script>
<style scoped lang="scss">
@import "assets/styles/variables";


.voting {
    width: 100%;
    display: flex;
    flex-direction: column;
    border-radius: 0px 0px 6px 6px;


    &.feedbacked {
        background-color: var(--chatfaq-color-primary-300);
        &.dark-mode {
            background-color: $chatfaq-color-primary-800 !important;
            color: $chatfaq-color-neutral-white !important;
        }
    }

    .feedback-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-left: 15px;
        .feedback-controls {
            margin-left: 15px;
            margin-right: 18px;
            display: flex;
        }
    }

    .separator-line {
        height: 1px;
        background-color: rgba(70, 48, 117, 0.2);
        align-content: center;
        text-align: center;
        margin: 15px;
        margin-top: 0px;
        margin-bottom: 8px;
        &.dark-mode {
            background-color: $chatfaq-color-neutral-purple;
        }
    }

    .feedback-input-wrapper {
        margin-top: 12px;
        margin: 15px;
        display: flex;
        border-radius: 4px;
        border: 1px solid $chatfaq-color-neutral-purple !important;
        background-color: $chatfaq-color-primary-200;
        box-shadow: 0px 4px 4px rgba(70, 48, 117, 0.1);

        &.dark-mode {
            background-color: $chatfaq-color-neutral-purple;
        }

        .feedback-input, .feedback-input:focus, .feedback-input:hover {
            width: 100%;
            border: 0;
            outline: 0;
            margin-left: 16px;
            background-color: $chatfaq-color-primary-200;
        }


        .feedback-input {
            height: 38px;
            border-radius: 10px;
            font: $chatfaq-font-caption-md;
            font-style: normal;

            &::placeholder {
                font-style: italic;
                color: rgb(2, 12, 28);
            }

            &.dark-mode {
                background-color: $chatfaq-color-neutral-purple;
                color: $chatfaq-color-primary-200;

                &::placeholder {
                    color: $chatfaq-color-neutral-white;
                }
            }
        }
    }

    .control {
        cursor: pointer;
        color: #9a8eb5;
        padding: 4px;
        margin-top: 2px;
        display: flex;
        &.dark-mode {
            color: $chatfaq-color-primary-300;
        }
        &.collapse {
            cursor: unset;
        }

    }

    .selected, .control:not(.collapse):hover {
        color: $chatfaq-color-primary-500;
        background: rgba(70, 48, 117, 0.1);
        border-radius: 2px;
        &.dark-mode {
            background-color: $chatfaq-color-primary-900;
        }
    }

    .quick-responses {
        margin-left: 15px;

        .quick-response {
            display: flex;
            align-items: center;
            margin-bottom: 15px;

            > span {
                margin-left: 6px;
            }
        }
    }

    .submit-feedback-wrapper {
        div {
            float: right;
            padding: 8px 16px;
            background: #463075;
            border-radius: 24px;
            margin-bottom: 16px;
            margin-right: 12px;
            color: white;
            font-weight: 600;
            cursor: pointer;
            &.dark-mode {
                background-color: $chatfaq-color-primary-900;
            }
        }
    }
}

</style>
