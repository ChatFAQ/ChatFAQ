<template>
    <MenuItem v-if="store.deleting">
        <i class="trash-icon"/>
        <span>{{ $t("confirm") }}</span>
        <div class="confirm-controls">
            <i class="close-icon" @click="() => {store.deleting = false}"/>
            <i class="check-icon" @click="deleteConversations"/>
        </div>
    </MenuItem>
    <MenuItem v-else @click="store.deleting = true; store.downloading = false;">
        <i class="trash-icon"/>
        <span v-if="store.selectedConversations.length">{{ $t("deleteselected") }}</span>
        <span v-else>{{ $t("clearhistory") }}</span>
    </MenuItem>
</template>

<script setup>
import { useGlobalStore } from "~/store";

const store = useGlobalStore();

import MenuItem from "~/components/left-menu/items/abs/MenuItem.vue";

async function deleteConversations() {
    const ids = store.selectedConversations.length ? store.selectedConversations : store.conversationsIds
    let response = await fetch(
        store.chatfaqAPI + `/back/api/broker/conversations/${ids}/`,
        {
            method: "DELETE",
            headers: {
              "Content-Type": "application/json",
            },
        }
    );
    await response.text();
    await store.gatherConversations()

    store.selectedConversations = []
    store.deleting = false
}

</script>


<style lang="scss" scoped>
@import "assets/styles/variables";

.trash-icon {
    content: $chatfaq-trash-icon;
}
.check-icon {
    content: $chatfaq-check-icon;
}
.close-icon {
    content: $chatfaq-close-icon;
}
.confirm-controls {
    width: 100%;
    display: flex;
    flex-direction: row-reverse;
}
</style>

