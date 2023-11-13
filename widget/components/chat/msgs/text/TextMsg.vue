<template>
    <div class="marked-down-content" :class="{ 'dark-mode': store.darkMode }" v-html="markedDown"></div>
    <span class="reference-index" :class="{ 'dark-mode': store.darkMode }" v-for="refIndex in data.referenceIndexes">{{ refIndex + 1 }}</span>
</template>

<script setup>
import { useGlobalStore } from "~/store";
import {computed} from "vue";

const store = useGlobalStore();
const props = defineProps(["data"]);


const markedDown = computed(() => {
    const linkRegex = /\[([^\]]+)\][ \n]*\(([^\)]+)\)/g;
    const res = props.data.payload.replace(linkRegex, '<a target="_blank" href="$2">$1</a>');
    return res
});

</script>
<style lang="scss">

.marked-down-content {
    display: inline;
    * {
        display: inline;
    }
    p {
        margin: 0;

        a {
            color: $chatfaq-color-chatMessageReference-text-light;
            background: $chatfaq-color-chatMessageReference-background-light;
            border-radius: 4px;
            padding: 0px 6px 0px 6px;
            text-decoration: none;
        }
    }
}
.reference-index {
    position: relative;
    top: -7px;
    margin-right: 2px;
    font-size: 8px;
    padding: 0px 3px 0px 3px;
    border-radius: 2px;
    color: $chatfaq-color-chatMessageReference-text-light;
    background: $chatfaq-color-chatMessageReference-background-light;
    &.dark-mode {
        background: $chatfaq-color-chatMessageReference-background-dark;
        color: $chatfaq-color-chatMessageReference-text-dark;
    }
}
</style>
