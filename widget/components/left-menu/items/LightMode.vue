<template>
    <MenuItem @click="store.darkMode = !store.darkMode">
        <i class="light-mode-icon" :class="{'dark-mode': store.darkMode}"/>
        <span v-if="!store.darkMode">Show dark mode</span>
        <span v-else>{{ $t("showlightmode") }}</span>
    </MenuItem>
</template>

<script setup>
import {useGlobalStore} from "~/store";
import MenuItem from "~/components/left-menu/items/abs/MenuItem.vue";

const store = useGlobalStore();

</script>


<style lang="scss" scoped>

.light-mode-icon {
    content: $chatfaq-moon-icon;

    &.dark-mode {
        content: $chatfaq-sun-icon;
    }
}
</style>

