<template>
    <div>
        <div class="marked-down-content" :class="{ 'dark-mode': store.darkMode }" v-html="markedDown"></div>
        <References :references="props.data.payload.references"></References>
    </div>
</template>

<script setup>
import { useGlobalStore } from "~/store";
import References from "~/components/chat/msgs/llm/References.vue";
const store = useGlobalStore();

const props = defineProps(["data"]);

const markedDown = computed(() => {
    const linkRegex = /\[([^\]]+)\][ \n]*\(([^\)]+)\)/g;
    const res = props.data.payload.model_response.replace(linkRegex, '<a target="_blank" href="$2">$1</a>');
    return res
});

</script>
<style lang="scss">
@import "assets/styles/variables";

.marked-down-content {
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
</style>

