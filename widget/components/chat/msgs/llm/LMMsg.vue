<template>
    <div>
        <div class="marked-down-content" v-html="markedDown"></div>
        <References :references="props.data.payload.references"></References>
    </div>
</template>

<script setup>
import References from "~/components/chat/msgs/llm/References.vue";
import { marked } from "marked";

const props = defineProps(["data"]);

const markedDown = computed(() => {
    return marked(props.data.payload.model_response);
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

