<template>
    <MenuItem @click="emitEventLogout">
        <Exit/>
        <span>{{ $t("logout") }}</span>
    </MenuItem>
</template>

<script setup>
import MenuItem from "~/components/left-menu/items/abs/MenuItem.vue";
import Exit from "~/components/icons/Exit.vue";

const event = new Event("chatfaq-logout");

function emitEventLogout() {
    document.dispatchEvent(event);
}


</script>


<style lang="scss" scoped>

</style>

