<template>
    <MenuItem>
        <i class="trash-icon"/>
        <span v-if="store.selectedConversations.length">{{ $t("deleteselected") }}</span>
        <span v-else>{{ $t("clearhistory") }}</span>
    </MenuItem>
</template>

<script setup>
import {useGlobalStore} from "~/store";

const store = useGlobalStore();

import MenuItem from "~/components/left-menu/items/abs/MenuItem.vue";
</script>


<style lang="scss" scoped>
@import "../assets/styles/variables";

.trash-icon {
    content: $chatfaq-trash-icon;
}
</style>

