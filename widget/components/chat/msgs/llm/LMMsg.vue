<template>
    <div>
        <div class="marked-down-content" :class="{ 'dark-mode': store.darkMode }" v-html="markedDown"></div>
        <span class="reference-index" :class="{ 'dark-mode': store.darkMode }" v-for="refIndex in data.referenceIndexes">{{ refIndex }}</span>
    </div>
</template>

<script setup>
import { marked } from "marked";
import { useGlobalStore } from "~/store";
const store = useGlobalStore();

const props = defineProps(["data"]);


const markedDown = computed(() => {
    let res = marked(props.data.payload.model_response);
    res = res.replace('<a href="', '<a target="_blank" href="')
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
        color: $chatfaq-color-primary-500;
        background: rgba(70, 48, 117, 0.1);
        border-radius: 4px;
        padding: 0px 6px 0px 6px;
        text-decoration: none;
    }
    &.dark-mode {
        a {
            background: $chatfaq-color-primary-900;
            color: $chatfaq-color-primary-200;
        }
    }
}
.reference-index {
    margin-right: 2px;
    font-size: 8px;
    padding: 0px 3px 0px 3px;
    border-radius: 2px;
    color: $chatfaq-color-primary-500;
    background: rgba(70, 48, 117, 0.1);
    &.dark-mode {
        background: $chatfaq-color-primary-900;
        color: $chatfaq-color-primary-200;
    }
}
</style>

