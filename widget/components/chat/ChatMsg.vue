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
                 v-if="props.data.type === MSG_TYPES.text"
                 :class="{
                [props.data.sender.type]: true,
                'is-last-of-type': props.isLastOfType,
                'dark-mode': store.darkMode,
            }">{{ props.data.payload }}</div>
            <div class="content"
                 v-if="props.data.type === MSG_TYPES.lm_generated_text"
                 :class="{
                [props.data.sender.type]: true,
                'is-last-of-type': props.isLastOfType,
                'dark-mode': store.darkMode,
            }">{{ props.data.payload.model_response }}</div>
<!--            <div v-if="props.isFirstOfType && props.data.sender.type === 'bot'" class="voting">
                <button @click="feedbacke(true)">Up</button>
                <button @click="feedbacke(false)">Down</button>
            </div>-->
        </div>
    </div>
</template>

<script setup>
import { useGlobalStore } from "~/store";

const props = defineProps(["data", "isLastOfType", "isFirstOfType", "isLast", "isFirst"]);
const store = useGlobalStore();
const feedbacked = ref(null)

const MSG_TYPES = {
	text: "text",
	lm_generated_text: "lm_generated_text",
}

async function feedback(positive) {
    const feedbackData = {
        message: props.data.id,
        value: positive ? 'positive' : 'negative',
        feedback: 'This is my feedback'
    };
    let method = "POST"
    let endpoint = '/back/api/broker/user-feedbacks/'
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

    }
    .message {
        width: fit-content;
        height: 100%;
        margin: 8px 5px 0px;
        display: flex;
        align-items: center;

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
        margin-left: 20px;
    }
}
</style>
