<template>
    <MenuItem>
        <i class="email-icon"/>
        <span>{{ $t("sendasummary") }}</span>
    </MenuItem>
</template>

<script setup>

import MenuItem from "~/components/left-menu/items/abs/MenuItem.vue";
</script>


<style lang="scss" scoped>
@import "../assets/styles/variables";

.email-icon {
    content: $chatfaq-mail-icon;
}
</style>

