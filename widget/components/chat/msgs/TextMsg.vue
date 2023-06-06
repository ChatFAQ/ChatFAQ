<template>
    <div class="content"
         v-if="props.data.type === MSG_TYPES.text || props.data.type === MSG_TYPES.lm_generated_text"
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
import UserFeedback from "~/components/chat/UserFeedback.vue";

const props = defineProps(["data", "isLastOfType", "isFirstOfType", "isLast", "isFirst"]);
const store = useGlobalStore();
const feedbacking = ref(null)

const MSG_TYPES = {
    text: "text",
    lm_generated_text: "lm_generated_text",
}


</script>
<style scoped lang="scss">
@import "assets/styles/variables";

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

    &.feedbacking {
        border-radius: 6px 6px 0px 0px !important;
        min-width: 100%;
    }
}
</style>
