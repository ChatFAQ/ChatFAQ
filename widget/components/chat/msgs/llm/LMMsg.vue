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
.marked-down-content{
    p {
        margin: 0;
    }
}
</style>

