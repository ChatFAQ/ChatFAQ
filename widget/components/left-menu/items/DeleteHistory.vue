<template>
    <MenuItem @click="deleteConversations">
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
    let response = await fetch(
        store.chatfaqAPI + `/back/api/broker/conversations`,
        {
            method: "DELETE",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
                ids: store.selectedConversations.length ? store.selectedConversations : store.conversationsIds
            })
        }
    );
    await response.json();
    await store.gatherConversations()
}

</script>


<style lang="scss" scoped>
@import "../assets/styles/variables";

.trash-icon {
    content: $chatfaq-trash-icon;
}
</style>

