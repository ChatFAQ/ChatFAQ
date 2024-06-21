<template>
    <MenuItem @click="store.darkMode = !store.darkMode">
        <Sun class="light-mode-icon"  v-if="store.darkMode"/>
        <Moon class="dark-mode-icon" v-else/>
        <span v-if="!store.darkMode">{{ $t("showdarkmode") }}</span>
        <span v-else>{{ $t("showlightmode") }}</span>
    </MenuItem>
</template>

<script setup>
import {useGlobalStore} from "~/store";
import MenuItem from "~/components/left-menu/items/abs/MenuItem.vue";
import Moon from "~/components/icons/Moon.vue";
import Sun from "~/components/icons/Sun.vue";

const store = useGlobalStore();

</script>


<style lang="scss" scoped>

.light-mode-icon {
    color: $chatfaq-moon-icon-color;

    &.dark-mode {
        color: $chatfaq-sun-icon-color;
    }
}
</style>

