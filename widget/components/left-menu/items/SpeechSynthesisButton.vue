<template>
    <MenuItem @click="toggleSpeechSynthesis">
        <MicrophoneDisabled v-if="store.speechSynthesisEnabled" />
        <Microphone class="microphone-icon" v-else />
        <span>{{ store.speechSynthesisEnabled ? $t("disablespeech") : $t("enablespeech") }}</span>
    </MenuItem>
</template>

<script setup>
import { useGlobalStore } from "~/store";
import MenuItem from "~/components/left-menu/items/abs/MenuItem.vue";
import Microphone from "~/components/icons/Microphone.vue";
import MicrophoneDisabled from "~/components/icons/MicrophoneDisabled.vue";

const store = useGlobalStore();

function toggleSpeechSynthesis() {
    store.speechSynthesisEnabled = !store.speechSynthesisEnabled;
}
</script>

<style lang="scss" scoped>
.volume-icon {
    color: $chatfaq-color-primary-500;
}

.microphone-icon {
    width: 16px;
    height: 16px;
}
</style> 