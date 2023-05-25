<template>
    <MenuItem class="item-wrapper" :editable="true" :class="{editing}">
        <i class="checkbox" :class="{'checked': selected}" @click="selected = !selected"/>
        <span class="item-title" v-if="!editing"> {{ timestampToSentence(title) }}</span>
        <textarea class="item-title-edit" v-else :value="timestampToSentence(title)"/>

        <div class="edit-controls" v-if="!editing">
            <i class="edit" @click="edit"/>
        </div>
        <div class="edit-controls" v-else>
            <i v-if="editing" class="check-icon" @click="deleteConversations"/>
            <i v-if="editing" class="close-icon" @click="() => {store.deleting = false}"/>
        </div>
    </MenuItem>
</template>

<script setup>
import {ref, watch} from 'vue';
import MenuItem from "~/components/left-menu/items/abs/MenuItem.vue";
import {useGlobalStore} from "~/store";

const store = useGlobalStore();

const props = defineProps(["title", "conversationId"]);

const selected = ref(false)
let editing = ref(false)

function edit() {
    editing.value = true
}

watch(selected, (newVal) => {
    if (newVal)
        store.selectedConversations.push(props.conversationId)
    else
        store.selectedConversations.splice(store.selectedConversations.indexOf(props.conversationId), 1);
})
defineExpose({selected})

function timestampToSentence(isoString) {
    return (new Date(isoString)).toString().split(" GMT")[0]
}

</script>


<style lang="scss" scoped>
@import "assets/styles/variables";

.item-wrapper {
    .checkbox {
        content: $chatfaq-checkbox-icon;

        &.checked {
            content: $chatfaq-checkbox-checked-icon;
        }
    }

    &:hover, &.editing {
        background-color: $chatfaq-color-primary-900;

        i.edit {
            content: $chatfaq-edit-icon;
        }
    }

    .edit-controls {
        display: flex;
        margin-left: 10px;

        .check-icon {
            content: $chatfaq-check-icon;
            margin-right: 4px;
        }

        .close-icon {
            content: $chatfaq-close-icon;
        }
    }
    .item-title {
        width: 120px;
    }
    .item-title-edit {
        width: 120px;
        background-color: unset;
        color: white;
        border: unset;
        outline: none;
        font-family: "Open Sans";
        font-size: 14px;
        resize: none;
        border: 1px solid $chatfaq-color-tertiary-blue-500;
        border-radius: 4px;
    }
}
</style>

