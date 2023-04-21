<template>
    <div class="message-wrapper">
        <div
            class="message"
            :class="{
                [props.data.transmitter.type]: true,
                'is-first-of-type': props.isFirstOfType,
                'is-first': props.isFirst,
                'is-last': props.isLast,
            }">
            <div class="content" :class="{
                [props.data.transmitter.type]: true,
                'is-last-of-type': props.isLastOfType,
                'dark-mode': store.darkMode
            }">{{ props.data.payload }}</div>
<!--            <div v-if="props.isFirstOfType && props.data.transmitter.type === 'bot'" class="voting">
                <button @click="vote(true)">Up</button>
                <button @click="vote(false)">Down</button>
            </div>-->
        </div>
    </div>
</template>

<script setup>
import { useGlobalStore } from "~/store";

const props = defineProps(["data", "isLastOfType", "isFirstOfType", "isLast", "isFirst"]);
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
    .content {
        border: solid 1px;
        border-radius: 20px;
        padding: 9px 15px 9px 15px;
        word-wrap: break-word;

        &.bot {
            border-color: $chatfaq-color-primary-500;
            color: $chatfaq-color-neutral-black;
            &.dark-mode {
                background-color: $chatfaq-color-neutral-black;
                border-color: $chatfaq-color-secondary-500;
                color: $chatfaq-color-neutral-white;
            }
            &.is-last-of-type {
                border-radius: 20px 20px 20px 0px;
            }
        }
        &.human {
            border: none;
            background-color: $chatfaq-color-primary-500;
            color: $chatfaq-color-neutral-white;

            &.is-last-of-type {
                border-radius: 20px 20px 0px 20px;
            }
        }

    }
    .message {
        width: fit-content;
        height: 100%;
        margin: 8px 5px 0px;
        max-width: 90%;
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
        }

        &.human {
            align-self: end;
            margin-right: 24px;
        }
    }

    .voting {
        margin-left: 20px;
    }
}
</style>
