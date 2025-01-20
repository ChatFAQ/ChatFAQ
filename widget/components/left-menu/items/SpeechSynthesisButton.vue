<template>
    <MenuItem @click="toggleSpeechSynthesis">
        <span>{{ store.speechSynthesisEnabled ? $t("disablespeech") : $t("enablespeech") }}</span>
    </MenuItem>
</template>

<script setup>
import { useGlobalStore } from "~/store";
import MenuItem from "~/components/left-menu/items/abs/MenuItem.vue";

const store = useGlobalStore();

function toggleSpeechSynthesis() {
    store.speechSynthesisEnabled = !store.speechSynthesisEnabled;
}
</script>

<style lang="scss" scoped>
.volume-icon {
    color: $chatfaq-color-primary-500;
}
</style> 