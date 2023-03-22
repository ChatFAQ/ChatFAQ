<template>
    <div class="history-item">
        <i class="checkbox" :class="{'checked': selected}" @click="selected = !selected"/> {{ timestampToSentence(title) }}
    </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps(["title", "conversationId"]);

const selected = ref(false)

function timestampToSentence(isoString) {
    return (new Date(isoString)).toString().split(" GMT")[0]
}

</script>


<style lang="scss" scoped>
@import "../assets/styles/variables";

.history-item {
    color: $chatfaq-color-neutral-white;
    /* identical to box height */

    letter-spacing: 0.5px;
    i {
        margin-right: 5px;
    }
    .checkbox {
        content: $chatfaq-checkbox;

        &.checked {
            content: $chatfaq-checkbox-checked;
        }
    }
}
</style>

