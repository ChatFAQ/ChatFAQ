<template>
    <MenuItem>
        <i class="plus"/>
        <span>{{ $t("newconversation") }}</span>
    </MenuItem>
</template>

<script setup>

import MenuItem from "~/components/left-menu/items/abs/MenuItem.vue";
</script>


<style lang="scss" scoped>
@import "../assets/styles/variables";

.plus {
    content: $chatfaq-plus-icon;
}
</style>

