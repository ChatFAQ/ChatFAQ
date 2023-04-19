<template>
    <div v-if="index && flatStacks[index - 1].transmitter.type == 'human'" class="voting">
        123
    </div>
    <div
        class="message"
        :class=" {
            [data.transmitter.type]: true,
            'is-last-of-type': props.isLastOfType,
            'is-first-of-type': props.isFirstOfType,
            'is-first': props.isFirst,
            'is-last': props.isLast,
            'dark-mode': store.darkMode
        }
    ">
        {{ data.payload }}
    </div>
</template>

<script setup>
import { useGlobalStore } from "~/store";

const props = defineProps(["data", "isLastOfType", "isFirstOfType", "isLast"]);
const store = useGlobalStore();

</script>
<style scoped lang="scss">
@import "assets/styles/variables";

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
    position: absolute;
}
</style>
