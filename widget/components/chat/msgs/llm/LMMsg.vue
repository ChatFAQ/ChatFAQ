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
const hightlight_light = "#4630751a"
const hightlight_dark = "#1A0438"

const markedDown = computed(() => {
    const hightlight = store.darkMode ? hightlight_dark : hightlight_light
    // regex for detecting and represent markdown links:
    const linkRegex = /\[([^\]]+)\][ \n]*\(([^\)]+)\)/g;
    let res = props.data.payload.model_response.replace(linkRegex, '<a target="_blank" href="$2">$1</a>');
    // regex for detecting and represent markdown lists:
    const listRegex = /(?:^|\n)(?:\*|\-|\d+\.)\s/g;
    res = res.replace(listRegex, '<br/>- ');
    // regex for detecting and represent the character: ` highlighting ex: bla bla `bla` bla:
    const highlightRegex = /`([^`]+)`/g;
    res = res.replace(highlightRegex, '<span style="background-color: '+ hightlight +'; padding: 0px 3px 0px 3px; border-radius: 2px;">$1</span>');
    // regex for detecting and representing codeblocks with tab  character:
    const codeBlockRegex = /(?:^|\n)(?:\t)([^\n]+)/g;
    const codeBlockRegex2 = /(?:^|\n)(?:    )([^\n]+)/g;
    res = res.replace(codeBlockRegex, '<span style="background-color: '+ hightlight +'; padding: 0px 3px 0px 3px; border-radius: 2px;">$1</span><br/>');
    res = res.replace(codeBlockRegex2, '<span style="background-color: '+ hightlight +'; padding: 0px 3px 0px 3px; border-radius: 2px;">$1</span><br/>');

    return res
});

</script>
<style lang="scss">

.marked-down-content {
    white-space: pre-wrap;
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

