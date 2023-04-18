<template>
    <MenuItem>
        <i class="checkbox" :class="{'checked': selected}" @click="selected = !selected"/>
        <span> {{ timestampToSentence(title) }}</span>
    </MenuItem>
</template>

<script setup>
import {ref, watch} from 'vue';
import MenuItem from "~/components/left-menu/items/abs/MenuItem.vue";
import {useGlobalStore} from "~/store";
const store = useGlobalStore();

const props = defineProps(["title", "conversationId"]);

const selected = ref(false)

watch(selected, (newVal) => {
    if (newVal)
        store.selectedConversations.push(props.conversationId)
    else
        store.selectedConversations.splice(store.selectedConversations.indexOf(props.conversationId), 1);
})
defineExpose({ selected })
function timestampToSentence(isoString) {
    return (new Date(isoString)).toString().split(" GMT")[0]
}

</script>


<style lang="scss" scoped>
@import "assets/styles/variables";

.checkbox {
    content: $chatfaq-checkbox-icon;

    &.checked {
        content: $chatfaq-checkbox-checked-icon;
    }
}
</style>

