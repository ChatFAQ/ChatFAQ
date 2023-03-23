<template>
    <MenuItem>
        <i class="checkbox" :class="{'checked': selected}" @click="selected = !selected"/>
        <span> {{ timestampToSentence(title) }}</span>
    </MenuItem>
</template>

<script setup>
import {ref} from 'vue';
import MenuItem from "~/components/left-menu/MenuItem.vue";

const props = defineProps(["title", "conversationId"]);

const selected = ref(false)

function timestampToSentence(isoString) {
    return (new Date(isoString)).toString().split(" GMT")[0]
}

</script>


<style lang="scss" scoped>
@import "../assets/styles/variables";

.checkbox {
    content: $chatfaq-checkbox;

    &.checked {
        content: $chatfaq-checkbox-checked;
    }
}
</style>

