<template>
    <MenuItem>
        <i class="download-icon"/>
        <span>{{ $t("downloadhistory") }}</span>
    </MenuItem>
</template>

<script setup>

import MenuItem from "~/components/left-menu/items/abs/MenuItem.vue";
</script>


<style lang="scss" scoped>
@import "assets/styles/variables";

.download-icon {
    content: $chatfaq-download-icon;
}
</style>

