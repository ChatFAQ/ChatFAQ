<template>
    <div class="marked-down-content" v-html="markedDown"></div>
</template>

<script setup>
const props = defineProps(["data"]);
import { marked } from "marked";

const markedDown = computed(() => {
    return marked(props.data.payload);
});

</script>
<style lang="scss">
.marked-down-content{
    p {
        margin: 0;
    }
}
</style>
