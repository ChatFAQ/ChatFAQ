<template>
    <div class="marked-down-content" :class="{ 'dark-mode': store.darkMode }" v-html="markedDown"></div>
</template>

<script setup>
import { useGlobalStore } from "~/store";
import { marked } from "marked";

const store = useGlobalStore();
const props = defineProps(["data"]);


const markedDown = computed(() => {
    let res = marked(props.data.payload);
    res = res.replace('<a href="', '<a target="_blank" href="')
    return res
});

</script>
<style lang="scss">
@import "assets/styles/variables";

.marked-down-content {
    p {
        margin: 0;

        a {
            color: $chatfaq-color-primary-500;
            background: rgba(70, 48, 117, 0.1);
            border-radius: 4px;
            padding: 0px 6px 0px 6px;
            text-decoration: none;
        }
    }
}
</style>
