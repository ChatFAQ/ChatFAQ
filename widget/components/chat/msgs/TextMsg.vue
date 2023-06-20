<template>
    <div class="msg"
         :class="{
        [props.data.sender.type]: true,
        'is-last-of-type': props.isLastOfType,
        'dark-mode': store.darkMode,
        'maximized': store.maximized,
        'feedbacking': feedbacking,
    }">{{ props.data.payload }}
    </div>
</template>

<script setup>
import {useGlobalStore} from "~/store";

const props = defineProps(["data", "isLastOfType", "feedbacking"]);
const store = useGlobalStore();


</script>
<style scoped lang="scss">
@import "assets/styles/variables";

.msg {
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

    &.feedbacking {
        border-radius: 6px 6px 0px 0px !important;
        min-width: 100%;
    }
}
</style>
