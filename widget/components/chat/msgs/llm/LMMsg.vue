<template>
    <div>
        <div class="marked-down-content" :class="{ 'dark-mode': store.darkMode }" v-html="markedDown"></div>
        <span class="reference-index" v-if="isLast" :class="{ 'dark-mode': store.darkMode }" v-for="refIndex in data.referenceIndexes">{{ refIndex + 1 }}</span>
    </div>
</template>

<script setup>
import { useGlobalStore } from "~/store";
import {computed} from "vue";

const store = useGlobalStore();

const props = defineProps(["data", "isLast"]);

const markedDown = computed(() => {
    const linkRegex = /\[([^\]]+)\][ \n]*\(([^\)]+)\)/g;
    const res = props.data.payload.model_response.replace(linkRegex, '<a target="_blank" href="$2">$1</a>');
    return res
});

</script>
<style lang="scss">
@import "assets/styles/variables";

.marked-down-content {
    display: inline;
    * {
        display: inline;
    }
    p {
        margin: 0;
    }
    a {
        color: $chatfaq-color-chatMessageReference-text-light;
        background: $chatfaq-color-chatMessageReference-background-light;
        border-radius: 4px;
        padding: 0px 6px 0px 6px;
        text-decoration: none;
    }
    &.dark-mode {
        a {
            background: $chatfaq-color-chatMessageReference-background-dark;
            color: $chatfaq-color-chatMessageReference-text-dark;
        }
    }
}
.reference-index {
    margin-right: 2px;
    font-size: 8px;
    padding: 0px 3px 0px 3px;
    border-radius: 2px;
    color: $chatfaq-color-chatMessageReference-text-light;
    background: $chatfaq-color-chatMessageReference-background-light;
    &.dark-mode {
        background: $chatfaq-color-chatMessageReference-text-dark;
        color: $chatfaq-color-chatMessageReference-background-dark;
    }
}
</style>

