<template>
    <div>
        {{ props.data.payload.model_response }}
        <References :references="props.data.payload.references"></References>
    </div>
</template>

<script setup>
import References from "~/components/chat/msgs/llm/References.vue";

const props = defineProps(["data"]);

</script>
