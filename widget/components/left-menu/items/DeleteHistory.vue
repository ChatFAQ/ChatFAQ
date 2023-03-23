<template>
    <MenuItem>
        <i class="trash-icon"/>
        <span>{{ $t("clearhistory") }}</span>
    </MenuItem>
</template>

<script setup>

import MenuItem from "~/components/left-menu/items/abs/MenuItem.vue";
</script>


<style lang="scss" scoped>
@import "../assets/styles/variables";

.trash-icon {
    content: $chatfaq-trash-icon;
}
</style>

