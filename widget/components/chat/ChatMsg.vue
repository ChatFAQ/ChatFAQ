<template>
    <div class="message-wrapper">
        <div
            class="message"
            :class=" {
                [props.data.transmitter.type]: true,
                'is-last-of-type': props.isLastOfType,
                'is-first-of-type': props.isFirstOfType,
                'is-first': props.isFirst,
                'is-last': props.isLast,
                'dark-mode': store.darkMode
            }
        ">
            <span class="content">{{ props.data.payload }}</span>
            <div v-if="props.isFirstOfType && props.data.transmitter.type === 'bot'" class="voting">
                <button @click="vote(true)">Up</button>
                <button @click="vote(false)">Down</button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { useGlobalStore } from "~/store";

const props = defineProps(["data", "isLastOfType", "isFirstOfType", "isLast"]);
const store = useGlobalStore();
const voted = ref(null)

async function vote(positive) {
    const voteData = {
        message: props.data.id,
        value: positive ? 'positive' : 'negative',
        feedback: 'This is my feedback'
    };
    let method = "POST"
    let endpoint = '/back/api/broker/votes/'
    if (voted.value) {
        voteData["id"] = voted.value
        method = "PATCH"
        endpoint = `${endpoint}${voteData["id"]}/`
    }
    const response = await fetch(store.chatfaqAPI + endpoint, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(voteData)
    })

    const res = await response.json();
    voted.value = res["id"]
}

</script>
<style scoped lang="scss">
@import "assets/styles/variables";

.message-wrapper {
    display: flex;
    flex-direction: column;

    .message {
        border: solid 1px;
        width: fit-content;
        margin: 8px 5px 0px;
        padding: 5px;
        border-radius: 20px;
        padding: 9px 15px 9px 15px;
        max-width: 90%;
        word-wrap: break-word;

        &.is-first-of-type {
            margin-top: 16px;
        }

        &.is-first {
            margin-top: 20px;
        }

        &.is-last {
            margin-bottom: 20px;
        }

        &.bot {
            border-color: $chatfaq-color-primary-500;
            color: $chatfaq-color-neutral-black;
            margin-left: 24px;

            &.is-last-of-type {
                border-radius: 20px 20px 20px 0px;
            }

            &.dark-mode {
                background-color: $chatfaq-color-neutral-black;
                border-color: $chatfaq-color-secondary-500;
                color: $chatfaq-color-neutral-white;
            }
        }

        &.human {
            border: none;
            background-color: $chatfaq-color-primary-500;
            color: $chatfaq-color-neutral-white;
            align-self: end;
            margin-right: 24px;

            &.is-last-of-type {
                border-radius: 20px 20px 0px 20px;
            }
        }
    }

    .voting {
    }
}
</style>
