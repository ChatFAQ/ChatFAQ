<template>
    <MenuItem
        class="item-wrapper conversation-loader"
        :editable="true"
        :class="{editing, open: store.selectedPlConversationId == props.platformConversationId}"
        @click="openConversation"
    >
        <Checkbox v-model="selected"/>
        <input v-if="!editing" disabled class="item-name disabled conversation-loader" rows="1" :value="name"/>
        <input v-else ref="itemTitleEdit" class="item-name edit" rows="1" :value="name" @keyup.enter="submit"/>

        <div class="edit-controls" v-if="!editing">
            <Edit class="edit" @click="edit"/>
        </div>
        <div class="edit-controls" v-else>
            <Check v-if="editing" class="check-icon" @click="submit"/>
            <Close v-if="editing" class="close-icon" @click="editing = false"/>
        </div>
    </MenuItem>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue';
import MenuItem from "~/components/left-menu/items/abs/MenuItem.vue";
import { useGlobalStore } from "~/store";
import Checkbox from "~/components/generic/Checkbox.vue";
import Check from "~/components/icons/Check.vue";
import Close from "~/components/icons/Close.vue";
import Edit from "~/components/icons/Edit.vue";

const store = useGlobalStore();

const props = defineProps(["name", "conversationId", "platformConversationId"])

const selected = ref(false)
let editing = ref(false)
let originalValue = props.name
let itemTitleEdit = ref(null)

function edit() {
    editing.value = true
    nextTick(() => {
        itemTitleEdit.value.focus()
        itemTitleEdit.value.selectionStart = itemTitleEdit.value.value.length;
    })
}

async function submit() {
    editing.value = false
    if (store.previewMode)
        return

    if (itemTitleEdit.value.value !== originalValue) {
        await store.renameConversationName(props.conversationId, itemTitleEdit.value.value)
    }
}


let counter = 0;
let timer = undefined;
function openConversation(ev) {
    if (store.previewMode)
        return

    if (ev.target.classList.contains("conversation-loader")) {
        counter++;
        if (counter === 1) {
            timer = setTimeout(() => {
                counter = 0;
                store.openConversation(props.platformConversationId)
            }, 200);
            return;
        }
        clearTimeout(timer);
        counter = 0;
        edit();
    }
}

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

.item-wrapper {
    display: flex;
    align-items: center;

    &.open {
        background-color: $chatfaq-color-menuItem-background-hover;
    }
    .edit {
        display: none;
    }
    &:hover, &.editing {
        background-color: $chatfaq-color-menuItem-background-hover;

        .edit {
            display: unset;
            color: $chatfaq-edit-icon-color;
        }
    }

    .edit-controls {
        display: flex;
        margin-left: auto;

        .check-icon {
            margin-right: 4px;
            color: $chatfaq-menu-check-icon-color;
        }
        .close-icon {
            color: $chatfaq-close-icon-color;
        }
    }

    .item-name {
        min-width: 30px;
        max-width: 155px;
        background-color: unset;
        color: $chatfaq-color-menu-text;
        border: unset;
        outline: none;
        font-family: "Open Sans";
        font-size: 14px;
        resize: none;
        border-radius: 4px;
        box-sizing: border-box;
        -webkit-box-sizing: border-box;
        -moz-box-sizing: border-box;
        text-align: left;
        border: 1px solid transparent;
        text-overflow: ellipsis;

        &.disabled {
            cursor: pointer;
            pointer-events: none;
        }

        &.edit {
            border: 1px solid $chatfaq-color-menuItem-border-edit;
            text-overflow: unset;
        }

    }
}
</style>

