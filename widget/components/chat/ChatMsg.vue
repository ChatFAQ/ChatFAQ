<template>
    <div class="message-wrapper">
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
                'feedbacked': feedbacked,
            }">{{ props.data.payload }}
            </div>
            <div v-if="props.isLastOfType && props.data.sender.type === 'bot'" class="voting"
                 :class="{'feedbacked': feedbacked}">
                <div class="separator-line" v-if="feedbacked"></div>
                <div class="feedback-top">
                    <div v-if="feedbacked">{{ $t('additionalfeedback') }}:</div>
                    <div class="feedback-controls">
                        <i class="thumb-up-icon" @click="userFeedback('positive')"/>
                        <i class="thumb-down-icon" @click="userFeedback('negative')"/>
                        <i class="copy-icon" @click="copy"/>
                    </div>
                </div>
                <div v-if="feedbacked">
                    <div class="feedback-input-wrapper" :class="{ 'dark-mode': store.darkMode }">
                        <input
                            :placeholder="$t('whatwastheissue')"
                            v-model="feedback"
                            class="feedback-input"
                            :class="{ 'dark-mode': store.darkMode }"
                            ref="chatInput"
                            @keyup.enter="userFeedback(feedbackValue.value)"
                        />
                    </div>
                    <div class="quick-responses">
                        <div class="quick-response">
                            <Checkbox v-model="selected" :dark="true"/>
                            <span>This is harmful/unsafe</span>
                        </div>
                        <div class="quick-response">
                            <Checkbox v-model="selected" :dark="true"/>
                            <span>This isn’t true</span>
                        </div>
                        <div class="quick-response">
                            <Checkbox v-model="selected" :dark="true"/>
                            <span>This isn’t helpful</span>
                        </div>
                    </div>
                    <div class="submit-feedback-wrapper">
                        <div @click="userFeedback(feedbackValue.value)"> {{ $t('submitfeedback') }} </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import {useGlobalStore} from "~/store";
import Checkbox from "~/components/generic/Checkbox.vue";

const props = defineProps(["data", "isLastOfType", "isFirstOfType", "isLast", "isFirst"]);
const store = useGlobalStore();
const feedbacked = ref(null)
const feedback = ref(null)
const feedbackValue = ref(null)

const MSG_TYPES = {
    text: "text",
    lm_generated_text: "lm_generated_text",
}

async function userFeedback(value) {
    feedbackValue.value = value
    const feedbackData = {
        message: props.data.id,
        value: value
    };
    if (feedback.value)
        feedbackData["feedback"] = feedback.value

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
}

</script>
<style scoped lang="scss">
@import "assets/styles/variables";

.message-wrapper {
    display: flex;
    flex-direction: column;

    .content {
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

        &.feedbacked {
            border-radius: 6px 6px 0px 0px !important;
            min-width: 550px;
            @media only screen and (max-width: $phone-breakpoint) {
                min-width: 300px;
            }
        }
    }

    .message {
        display: flex;
        flex-direction: column;
        align-items: center;

        width: fit-content;
        height: 100%;
        margin: 8px 5px 0px;


        &.is-first-of-type {
            margin-top: 16px;
        }

        &.is-first {
            margin-top: 30px;
        }

        &.is-last {
            margin-bottom: 20px;
        }

        &.bot {
            margin-left: 24px;
            margin-right: 86px;

            &.maximized {
                margin-right: 404px;
            }
        }

        &.human {
            align-self: end;
            margin-right: 24px;
            margin-left: 86px;

            &.maximized {
                margin-left: 404px;
            }
        }
    }

    .voting {
        width: 100%;
        display: flex;
        flex-direction: column;

        .feedback-top {
            display: flex;
            align-items: center;
            margin-left: 15px;
        }

        .feedback-controls {
            float: right;
            margin-left: auto;
            margin-right: 18px;
        }

        .separator-line {
            height: 1px;
            background-color: rgba(70, 48, 117, 0.2);
            align-content: center;
            text-align: center;
            margin: 15px;
            margin-top: 0px;
            margin-bottom: 8px;
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
                background-color: $chatfaq-color-primary-800;
                border: 1px solid $chatfaq-color-primary-900 !important;
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
                    background-color: $chatfaq-color-primary-800;
                    color: $chatfaq-color-primary-200;

                    &::placeholder {
                        color: $chatfaq-color-neutral-white;
                    }
                }
            }
        }

        i {
            margin: 4px;
            margin-top: 6px;
        }

        .thumb-up-icon {
            content: $chatfaq-thumb-up-icon;
            cursor: pointer;
        }

        .thumb-down-icon {
            content: $chatfaq-thumb-down-icon;
            cursor: pointer;
        }

        .copy-icon {
            content: $chatfaq-copy-icon;
            cursor: pointer;
        }

        &.feedbacked {
            background-color: var(--chatfaq-color-primary-300);
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
        }
    }
}
</style>
