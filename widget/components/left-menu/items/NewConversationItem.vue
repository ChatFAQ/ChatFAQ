<template>
    <MenuItem @click="store.createNewConversation">
        <Plus class="plus"/>
        <span>{{ $t("newconversation") }}</span>
    </MenuItem>
</template>

<script setup>

import MenuItem from "~/components/left-menu/items/abs/MenuItem.vue";
import { useGlobalStore } from "~/store";
import Plus from "~/components/icons/Plus.vue";

const store = useGlobalStore();

</script>


<style lang="scss" scoped>

.plus {
    color: $chatfaq-plus-icon-color;
}
</style>

