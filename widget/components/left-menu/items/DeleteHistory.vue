<template>
    <MenuItem v-if="store.deleting">
        <i class="trash-icon"/>
        <span>{{ $t("confirm") }}</span>
        <div class="confirm-controls">
            <Close class="close-icon" @click="() => {store.deleting = false}"/>
            <Check class="check-icon" @click="deleteConversations"/>
        </div>
    </MenuItem>
    <MenuItem v-else @click="store.deleting = true; store.downloading = false;">
        <i class="trash-icon"/>
        <span v-if="store.selectedConversations.length">{{ $t("deleteselected") }}</span>
        <span v-else>{{ $t("clearhistory") }}</span>
    </MenuItem>
</template>

<script setup>
import Check from "~/components/icons/Check.vue";
import Close from "~/components/icons/Close.vue";
import { useGlobalStore } from "~/store";

const store = useGlobalStore();

import MenuItem from "~/components/left-menu/items/abs/MenuItem.vue";

async function deleteConversation(id) {
    if (store.previewMode)
        return

    await fetch(
        store.chatfaqAPI + `/back/api/broker/conversations/${id}/`,
        {
            method: "DELETE",
            headers: {
              "Content-Type": "application/json",
            },
        }
    );
}

async function deleteConversations() {
    if(store.previewMode)
        return

    const ids = store.selectedConversations.length ? store.selectedConversations : store.conversationsIds
    await Promise.all(ids.map(id => deleteConversation(id)))
    await store.gatherConversations()

    store.selectedConversations = []
    store.deleting = false
}

</script>


<style lang="scss" scoped>

.trash-icon {
    content: $chatfaq-trash-icon;
}
.confirm-controls {
    width: 100%;
    display: flex;
    flex-direction: row-reverse;
    .check-icon {
        color: $chatfaq-check-icon-color;
    }
    .close-icon {
        color: $chatfaq-close-icon-color;
    }
}
</style>

